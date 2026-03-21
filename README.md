# HA Supertronics HAT UPS X120x

A practical Home Assistant integration for the SupTronics X1200, X1201 and X1202 UPS HAT on Raspberry Pi 5.

This project started from a simple goal: make the board behave the way people actually expect it to behave inside Home Assistant. That means exposing the useful battery data, keeping the setup straightforward, and fixing the annoying part where charging does not stop automatically at full charge.

It keeps the Home Assistant domain `suptronics_ups_x120x` for compatibility with existing installations, but the project identity, packaging and behavior are independent from the older community integration.

Referenced projects:

- Community integration: `soukal24/ha_suptronics_ups_x120x`
- Manufacturer reference scripts: `suptronics/x120x`

## Why this version exists

The original references are helpful, but they leave a few real-world gaps when you actually run the HAT every day on a Raspberry Pi:

- charging control exists, but not as a polished Home Assistant workflow
- older setups can leave you with partial config entries
- GPIO behavior can vary across system updates and library versions
- diagnosing AC detection issues is difficult without extra visibility

This project focuses on that real hardware experience, not just the happy path.

## What makes this integration different

- Automatic charge stop/resume with hysteresis
- Manual charging control from Home Assistant
- Configurable charge thresholds from the UI
- AC power detection with raw GPIO diagnostics
- Compatibility fixes for older config entries
- Better resilience across `gpiod` behavior changes on Raspberry Pi 5 systems
- UI config flow and options flow

Default automatic charging policy:

- Stop charging at `100%`
- Resume charging at `95%`

## Hardware defaults

Values derived from the manufacturer project and validated during Raspberry Pi 5 testing:

- I2C address: `0x36`
- I2C bus: `1`
- AC power detection pin: `GPIO 6`
- Charge control pin: `GPIO 16`
- GPIO chip: `/dev/gpiochip0`

## Entities exposed

- Battery percentage sensor
- Battery voltage sensor
- Battery state sensor
- AC power binary sensor
- Manual charging switch
- Automatic charging switch
- Stop-charge threshold number
- Resume-charge threshold number

## Install with HACS

This repository is ready to use as a HACS custom repository.

1. Open HACS.
2. Go to `Integrations`.
3. Open the menu and choose `Custom repositories`.
4. Add `https://github.com/Rooterts/HA_supertronics_hat_ups_x120x`.
5. Select `Integration`.
6. Install `HA Supertronics HAT UPS X120x`.
7. Restart Home Assistant.
8. Go to `Settings -> Devices & Services -> Add Integration`.
9. Search for `HA Supertronics HAT UPS X120x`.

## Manual installation

1. Copy `custom_components/suptronics_ups_x120x` into your Home Assistant `custom_components` directory.
2. Restart Home Assistant.
3. Add the integration from the UI.

## Updating from the older integration

Because both projects share the same Home Assistant domain, do not keep both installed at the same time.

If you are migrating from `soukal24/ha_suptronics_ups_x120x`:

1. Remove or replace the existing `custom_components/suptronics_ups_x120x` folder.
2. Restart Home Assistant.
3. If the integration appears unavailable, remove the old config entry and add it again.

If you previously used YAML snippets, remove any old `suptronics_ups_x120x:` entries before testing this version.

## Raspberry Pi notes

Before testing, make sure:

- I2C is enabled on the Raspberry Pi
- Home Assistant can access `/dev/i2c-1`
- Home Assistant can access `/dev/gpiochip0`

On Home Assistant OS, Container, or Supervised installs, GPIO and I2C access depends on how the host is exposed to Home Assistant.

## Development

Basic local checks:

```bash
python -m compileall custom_components
python -m unittest discover -s tests
```

## HACS status

This repository can already be installed through HACS as a custom repository.

To be included in the default HACS catalog, the next steps are:

- Keep the repository public on GitHub
- Pass HACS validation
- Pass Hassfest
- Create GitHub releases
- Submit the repository to `hacs/default`

## License note

This repository contains original integration code inspired by the upstream projects above. Review upstream licensing separately before redistributing combined work publicly.
