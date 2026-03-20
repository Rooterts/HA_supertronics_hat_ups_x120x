# HA_supertronics_hat_ups_x120x

Custom HACS integration for Home Assistant to monitor and control the SupTronics X1200, X1201 and X1202 UPS HAT for Raspberry Pi 5.

This project keeps the Home Assistant domain `suptronics_ups_x120x` for compatibility with the existing community integration, but improves the charging behavior based on the manufacturer documentation and scripts.

Referenced projects:

- Community integration: `soukal24/ha_suptronics_ups_x120x`
- Manufacturer reference scripts: `suptronics/x120x`

## Main improvement

The manufacturer documents charge control through `GPIO 16`:

- `pinctrl set 16 op dh`: disable charging
- `pinctrl set 16 op dl`: enable charging

This repository adds automatic charging control inside Home Assistant using hysteresis:

- Stop charging at a configurable upper threshold
- Resume charging at a configurable lower threshold
- Avoid fast on/off oscillation around 100%

Default values:

- Stop charging at `100%`
- Resume charging at `95%`

## Hardware defaults

Values derived from the manufacturer project and docs:

- I2C address: `0x36`
- I2C bus: `1`
- AC power detection pin: `GPIO 6`
- Charge control pin: `GPIO 16`
- GPIO chip: `/dev/gpiochip0`

## Features

- Battery percentage sensor
- Battery voltage sensor
- Battery state sensor
- AC power binary sensor
- Manual charging switch
- Automatic charging switch
- Configurable stop-charge threshold
- Configurable resume-charge threshold
- UI config flow and options flow

## HACS installation

1. Open HACS.
2. Go to `Integrations`.
3. Open the menu and choose `Custom repositories`.
4. Add this repository URL and select `Integration`.
5. Install `HA Supertronics HAT UPS X120x`.
6. Restart Home Assistant.
7. Go to `Settings -> Devices & Services -> Add Integration`.
8. Search for `Suptronics UPS X120x`.

## Manual installation

1. Copy [custom_components/suptronics_ups_x120x](/home/rooterts/Projects/ZGo/custom_components/suptronics_ups_x120x) into your Home Assistant `custom_components` directory.
2. Restart Home Assistant.
3. Add the integration from the UI.

## Updating from the older integration

Because both integrations use the same domain, you should not keep both copies installed at the same time.

If you already have the older `soukal24/ha_suptronics_ups_x120x` version installed:

1. Remove or replace the existing `custom_components/suptronics_ups_x120x` folder.
2. Restart Home Assistant.
3. If Home Assistant shows the integration as unavailable, remove the old config entry and add it again.

If you previously used YAML snippets, remove those old `suptronics_ups_x120x:` entries before testing this version.

## Raspberry Pi notes

Before testing, make sure:

- I2C is enabled on the Raspberry Pi
- Home Assistant can access `/dev/i2c-1`
- Home Assistant can access `/dev/gpiochip0`

On Home Assistant OS, GPIO/I2C access depends on your installation method and host permissions.

## Development

Basic local checks:

```bash
python -m compileall custom_components
python -m unittest discover -s tests
```

## License note

This repository contains original integration code inspired by the two referenced upstream projects. Review upstream licensing separately before redistributing combined work publicly.
