"""
Command-Line Interface

CLI for HL7 EU Gazelle FHIR Validator.
"""

import sys
from pathlib import Path
from typing import Optional
import click
from rich.console import Console
from rich.table import Table
from loguru import logger

from .validator.validator import FHIRValidator
from .utils.config import Config
from .utils.logger import setup_logger
from .utils.exceptions import ValidationError, ConfigurationError

console = Console()


@click.group()
@click.version_option(version="0.1.0")
@click.option("--debug", is_flag=True, help="Enable debug mode")
@click.option("--config", type=click.Path(exists=True), help="Path to .env config file")
@click.pass_context
def cli(ctx, debug, config):
    """
    HL7 EU Gazelle FHIR Validator

    Validates FHIR bundles and resources against EU implementation guides.
    """
    try:
        # Load configuration
        config_obj = Config(env_file=Path(config) if config else None)
        if debug:
            config_obj.DEBUG = True
            config_obj.LOG_LEVEL = "DEBUG"

        # Setup logging
        setup_logger(config_obj)

        # Store config in context
        ctx.ensure_object(dict)
        ctx.obj["config"] = config_obj

    except ConfigurationError as e:
        console.print(f"[red]Configuration Error:[/red] {e}")
        sys.exit(1)


@cli.command()
@click.argument("resource_path", type=click.Path(exists=True))
@click.option("--profile", "-p", help="FHIR profile URL")
@click.option("--validator", "-v", help="EVS validator name")
@click.option("--output", "-o", type=click.Path(), help="Output file for results")
@click.option("--format", "-f", type=click.Choice(["json", "console"]), default="console")
@click.option("--strict", is_flag=True, help="Treat warnings as errors")
@click.pass_context
def validate(ctx, resource_path, profile, validator, output, format, strict):
    """
    Validate a FHIR resource or bundle.

    RESOURCE_PATH: Path to FHIR resource file (JSON)

    Examples:

        hl7-eu-validator validate patient.json

        hl7-eu-validator validate bundle.json --profile hospital-discharge

        hl7-eu-validator validate lab-report.json --output report.json --format json
    """
    config = ctx.obj["config"]

    try:
        with console.status("[bold green]Validating FHIR resource..."):
            # Initialize validator
            validator_instance = FHIRValidator(config=config)

            # Perform validation
            report = validator_instance.validate(
                resource=Path(resource_path), profile=profile, validator=validator
            )

            validator_instance.close()

        # Check strict mode
        if strict and report.warning_count > 0:
            report.is_valid = False

        # Output results
        if format == "json":
            import json

            result = json.dumps(report.to_dict(), indent=2)
            if output:
                Path(output).write_text(result)
                console.print(f"[green]Results saved to {output}[/green]")
            else:
                console.print(result)
        else:
            # Console output
            console.print(report.to_console(colorize=True))

            if output:
                Path(output).write_text(report.to_console(colorize=False))
                console.print(f"[dim]Results also saved to {output}[/dim]")

        # Exit code
        sys.exit(0 if report.is_valid else 1)

    except ValidationError as e:
        console.print(f"[red]Validation Error:[/red] {e}")
        sys.exit(1)
    except Exception as e:
        logger.exception("Unexpected error during validation")
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)


@cli.command()
@click.argument("directory", type=click.Path(exists=True))
@click.option("--profile", "-p", help="FHIR profile URL for all resources")
@click.option("--output", "-o", type=click.Path(), help="Output directory for results")
@click.option("--pattern", default="*.json", help="File pattern to match")
@click.pass_context
def validate_dir(ctx, directory, profile, output, pattern):
    """
    Validate all FHIR resources in a directory.

    DIRECTORY: Path to directory containing FHIR resources

    Examples:

        hl7-eu-validator validate-dir ./resources/

        hl7-eu-validator validate-dir ./bundles/ --pattern "*.bundle.json"
    """
    config = ctx.obj["config"]
    dir_path = Path(directory)
    resource_files = list(dir_path.glob(pattern))

    if not resource_files:
        console.print(f"[yellow]No files matching '{pattern}' found in {directory}[/yellow]")
        return

    console.print(f"[cyan]Found {len(resource_files)} resources to validate[/cyan]")

    try:
        validator_instance = FHIRValidator(config=config)
        results = []

        for resource_file in resource_files:
            console.print(f"\n[bold]Validating:[/bold] {resource_file.name}")
            try:
                report = validator_instance.validate(resource=resource_file, profile=profile)
                results.append((resource_file.name, report))

                status = "✅ PASSED" if report.is_valid else "❌ FAILED"
                console.print(f"  Status: {status}")

            except Exception as e:
                console.print(f"  [red]Error: {e}[/red]")
                results.append((resource_file.name, None))

        validator_instance.close()

        # Summary table
        _print_summary_table(results)

    except Exception as e:
        logger.exception("Unexpected error during batch validation")
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)


@cli.command()
@click.option("--filter", "-f", help="Filter validators by keyword")
@click.pass_context
def list_validators(ctx, filter):
    """
    List available EVS validators.

    Examples:

        hl7-eu-validator list-validators

        hl7-eu-validator list-validators --filter laboratory
    """
    config = ctx.obj["config"]

    try:
        validator = FHIRValidator(config=config)
        validators = validator.list_validators()
        validator.close()

        if filter:
            validators = [v for v in validators if filter.lower() in v.lower()]

        if validators:
            table = Table(title="Available EVS Validators")
            table.add_column("Validator Name", style="cyan")

            for v in validators:
                table.add_row(v)

            console.print(table)
        else:
            console.print("[yellow]No validators found[/yellow]")

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)


def _print_summary_table(results):
    """Print summary table of batch validation results."""
    table = Table(title="Validation Summary")
    table.add_column("Resource", style="cyan")
    table.add_column("Status", justify="center")
    table.add_column("Errors", justify="right", style="red")
    table.add_column("Warnings", justify="right", style="yellow")

    for filename, report in results:
        if report:
            status = "✅" if report.is_valid else "❌"
            errors = str(report.error_count)
            warnings = str(report.warning_count)
        else:
            status = "⚠️"
            errors = "-"
            warnings = "-"

        table.add_row(filename, status, errors, warnings)

    console.print("\n")
    console.print(table)


def main():
    """Entry point for CLI."""
    cli(obj={})


if __name__ == "__main__":
    main()
