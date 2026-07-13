#!/usr/bin/env python3
"""
US Visa Alert System - Entry Point

Run this script to start the visa monitoring system.
"""

from app.main import VisaAlertSystem


def main():
    """Main entry point."""
    try:
        system = VisaAlertSystem()
        system.start_continuous()
    except KeyboardInterrupt:
        print("\n\nSystem shutdown requested by user.")
    except Exception as e:
        print(f"\nFatal error: {e}")
        raise


if __name__ == "__main__":
    main()
