# Foreman 0.4 (closed beta)
_Monitor your rigs on Telegram._

## Functions

**Foreman** is a client/server software that allows you to
monitor your mining rig performances right on Telegram.

* **Active dashboard:** A dashboard will always be waiting for you
when you enter the chat with Foreman. The dashboard is updated
every now and then, allowing you to monitor global hashrate and
GPU hashrate, temperature and fan speed.

* **Timeout alerts:** If your rig doesn't report for some time, the
bot sends you an alert, letting you know for how long your machine
has been inactive.

* **⭐ Advanced alerts:** _Premium_ users can set customized alerts based
on thresholds for global hashrate, GPU failure, GPU hashrate and temperature.

* **⭐ Remote commands:** In case of failure, _Premium_ users can restart
the miner (process) or execute a customized bash script on their machine
(allowing, but not limiting, them to reboot or turn off the machine).

## Prerequisites

* Rig must be running **Claymore** miner

* Claymore configuration should **allow remote monitoring**:
  >
  >    `-mport 3333` sets the monitoring port to `3333` and activates remote control.
  If you are not going to use remote commands, you can set it to `-3333` to activate monitoring
  but disable remote control.
  >
  >    `-mpsw pass` sets a password for remote monitoring and control.

* You must have a Telegram account

## Usage

### 1. Configuration

In your configuration file, you have to set the following parameters:

`user: id:` The identifier of your Telegram account. To know your
identifier, simply send `/user_id` to Foreman, in private.

`user: key:` Your secret licence key. Has to be in the form: `"RigName:Key"` (example: `"RigA:123456789"`).

`user: server:` This is the server your rig will be reporting to. Default value has to be used, unless stated otherwise.

`miner: ip:` The IP address of your miner on local area network.
If the software is running on the same machine as the miner, `"127.0.0.1"` can be used.

`miner: port:` The port on which your mining software allowed monitoring,
as set in your miner configuration file (by default, Claymore uses port `3333`).

`params: uptime_min:` This is the minimum uptime of your rig
_before_ the software starts checking for timeout or failures.
The minimum value you can set is `60` seconds.

`params: failure_min:` Time to wait for your machine to report.
Passed this time, a `TIMEOUT` alert will be sent.
The minimum value you can set is `180` seconds (3 minutes).
Recommended and default value is `300` seconds (5 minutes).

⭐ `params: PERF_LESS_THAN:` The desired minimum total hashrate
of your rig. This is for primary mining only (not dual).
Value should be in kH/s (example: if your rig operates at 120 MH/s,
and you want to be alerted if it performs at less than
115 MH/s, set this parameter to `115000` kH/s).
When your rig doesn't perform as well as your desired value, an alert is sent, with options to restart miner or reboot the machine.

⭐ `params: UNIT_COUNT_LESS_THAN:` Number of operating GPU in your rig (primary mining only).
If you have 6 GPU in your rig, you may want to set the value to `6`. This way, if any GPU fails,
an alert would be sent to you. If one or more of your units constantly fail, and you want to avoid
receiving this alert often, set it to the number of units that don't usually fail. You get the idea :)
When this error is raised, an alert is sent, with options to restart miner or reboot the machine.

⭐ `params: UNIT_PERF_LESS_THAN:` Array of one or more minimum hashrate values for your units.
This is for primary mining only (dual mining is not supported).
You can set one value for all your GPU units (example: `[28000]`),
or set a custom value for each unit (example: `[28000, 28000, 28000, 27000, 9500, 9500]`).
When a unit's performance is below the threshold,
an alert is sent, with options to restart miner or reboot the machine.

⭐ `params: UNIT_TEMP_GREATER_THAN:` Array of one or more temperature threshold values for your units.
You can set one value for all your units (example: `[83]` for 83 °C),
or set a custom value for each GPU unit (example: `[75, 75, 75, 80, 83, 83]`).

_Parameters marked with a star (⭐) are for **Premium** users only._

### 2. Launch the software at startup

**Windows**

Easily create a shortcut to this software and store it inside `%AppData%\Microsoft\Windows\Start Menu\Startup`

You can edit the shortcut's properties to make it launch minimized, as you can change fond and window size.

**Linux**

A `.service` file is provided.

Follow these steps, _as super user (`sudo -s`)_, _inside the program folder_, to register it:

1. `cp ./foreman.service /lib/systemd/system/foreman.service`
1. `chmod 644 /lib/systemd/system/foreman.service`
1. `chmod +x Foreman.py`
1. `systemctl daemon-reload`
1. `systemctl enable foreman.service`
1. `systemctl start foreman.service`

To check service status, run: `systemctl status foreman.service`

To stop the software, run: `systemctl stop foreman.service`

To remove the service, run: `systemctl disable Foreman.service`

Feel free to geek and create your own service or change service settings.

### 3. Telegram bot

The Telegram bot _is_ your dashboard.
It will create a persistent message,
updated with the latest information from your machine.

When an error occurs, an alert message is send to you in private.

Error messages contain useful information about the state of your rig.
Although more information are on the dashboard, that stays up to date.

Alert messages allow you to perform simple maintenance operations on your machine:

* **Restart:** This order will ask the miner (Claymore) to restart its thread.
It is the equivalent of closing the miner thread manually and launching it again.

* **Reboot:** Executes a batch script on your machine.
The batch script has to be named `reboot.bat` on Windows and `reboot.sh` on Linux-based OS.
The script supposedly contains commands to _force_ reboot your machine.
Although it can be used to force shut down, or perform more complex actions.
An example is provided with this software. _Geek it!_

**A note on persistent dashboard:**
For an obscure reason, sometimes, Telegram disallows editing the persistent message.
When this happens, the bot will send you a message,
explaining the situation and allowing you to request a new dashboard message.

**Other useful commands:**

`/reset_dashboards` will request a new dashboard for each rig. This can be used for _cleaning_ purpose
(after clearing chat history with the bot, for example). Please, do not overuse it.

`/user_id` informs you of your Telegram unique identifier.
It can be useful to set up the configuration file
or simply for your own usage.

`/help` A Help button will always be shown on your persistent dashboard.
However, you can still ask for help by sending the `/help` command.

`/about` Shows information about the bot, such as version and copyright.

`/licence` Shows information about licence keys and how to acquire a new licence.

## Licence information

The licence keys provided to you are personal. Keep them secret.

Each machine requires a licence key.
If you have many rigs to monitor, request a key bundle.

Requesting a licence key is actually done through a private message to the developer.
Before doing so, please use `/licence` in private with the bot.

## Legal

The _client_ part of this software is distributed under the terms of The Unlicence and its code is made public.

Even though we recommand _not_ to change the behavior of this software, you are granted the freedom to edit it.
You can modify the way this software communicates with the miner, or even the way it executes the given restart and reboot orders.

However, the API information will not be provided,
although it can be easily understood through the code.
We recommend sending a request every minute at most,
for sending successive fast requests would result in your IP being banned and your user keys being lost.

The _Telegram Bot_ and _server-side_ software are proprietary software and fall under the Copyright law.
