# PV Simulator


## Getting Started


### Prerequisites

docker >= 17.05 (needs this version, to use multi-stage builds)
docker-compose  (to build and run images)

### Components(containers)

#### Grid

Grid is a Kombu Producer/Consumer, that send and receives events/commands to the Rabbitmq broker.
It is started/stoped sending commands to the command channel, that is connected to the SocketIO.

#### PV

PV tries to simulate a photovoltaic cell, in a normal day. It uses 2 rects and one parabola to get
an acurate simulation, maybe is enought to use sine(evaluate).

This container also stores the simulation in a csv file, in ./files/, this file also can be downloaded
from Control Panel.

#### API

This container only starts a socketio server in flask, but al the events are sent from PV, using
socketio multiprocess support, using rabbitmq.

#### Static - nginx and react application(Control Panel)

This is a multi-stage build container, it builds and embeds the js application in the web root.
This container is not only used for static content, also as a proxy to the api.
The frontend application, is built using react js, connecting to the api container using socketio.
This was only tested in google chrome.

## Running the tests

All the tests use pytest, and pytest-cov and run in docker build stage.


## Deployment

To run this code, you only need to run, docker-compose up and after every container is built and started,
go to the Control Panel in http://HOST:4242/, ex. "http://localhost:4242/" if you it's running in
the same machine of your browser.

## Usage

When you hit the browser, you'll see something like the screenshot above,
in the top left corner, you have an start button, that start the simulation,
when the simulation ends, at the end of the simulation, the "Simulation Log" should be active,
so you can download a csv of the result of the simulation.

The offset slider at the right, let you change the "regular power consumition", on the fly,
when the simulator is started, it selects a random value for it, from 0 to 9000.


![screenshot](https://raw.githubusercontent.com/roger/pvsim/master/image.png)

## Built With

* [Flask](http://flask.pocoo.org/) - The web framework used.
* [Flask-SocketIO](https://github.com/miguelgrinberg/Flask-SocketIO) - Socket.IO integration for Flask.
* [React](https://reactjs.org/) - A JavaScript library for building UI

## Authors

* **Roger Duran**

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE.md](LICENSE.md) file for details
