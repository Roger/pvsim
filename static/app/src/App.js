import io from 'socket.io-client';

import React, { Component } from 'react';

import { Slider } from "@blueprintjs/core";

import Nav from './Nav';
import Chart from './Chart';
import Logger from './Logger';
import './App.css';


const namespace = ':4242/reads';
const socket = io.connect(namespace);


class App extends Component {
  constructor(props) {
    super(props)
    this.state = {
      data: [],
      all: [],
      offset: 0,
      simulationEnded: false,
    }
    this.timeout = null;
  }
  componentDidMount() {
    // ask the server for the info
    socket.emit('command', 'info')

    // listen to commands sent from the server
    socket.on('command', (msg) => {
      if (msg.type === 'offset') {
        this.setState({ offset: msg.value })
      } else if (msg.type === 'end') {
        this.setState({ simulationEnded: true })
      } else if (msg.type === 'start') {
        this.setState({
          data: [],
          simulationEnded: false,
        })
      } else if (msg.type === 'info') {
        this.setState({
          offset: msg.offset,
          sim_type: msg.sim_type,
          date: msg.current_time,
        })
      }
    })

    // listen for event in meter
    socket.on('read', (msg) => {
      const date = new Date(msg['time'])
      const newMsg = {...msg}

      const all = [...this.state.all].reverse()

      // filter points for the graph
      if (date.getSeconds() === 0 && date.getMinutes() % 10 === 0) {
        const data = [...this.state.data].reverse()
        this.setState({
          data: [newMsg, ...data].reverse(),
          all: [newMsg, ...all].reverse(),
        })
      } else {
        this.setState({ all: [newMsg, ...all].reverse() })
      }
    })
  }

  onRestart = () =>  socket.emit('command', 'start')
  onChangeOffset = (value) => this.setState({ offset: value })
  onUpdateOffset = value => socket.emit('command', 'offset', value)

  render() {
    // latest 5 log entries
    const logData = this.state.all.slice(this.state.all.length-5, this.state.all.length).reverse()
                                                                                              
    return (
      <div className="container">
        <Nav restart={this.onRestart} shownDownload={this.state.simulationEnded} />
        <div className="content">
          <div style={{ display: 'flex' }}>
            <div>
              <Chart data={this.state.data} simulationEnded={this.state.simulationEnded} />
            </div>
            <div>
              <Slider
                  className="offset-slide"
                  min={0}
                  max={9000}
                  stepSize={100}
                  labelStepSize={1000}
                  onChange={this.onChangeOffset}
                  onRelease={this.onUpdateOffset}
                  value={this.state.offset}
                  vertical
              />
              <strong>Offset</strong>
            </div>
          </div>

          <Logger data={logData} />

        </div>

      </div>
    );
  }
}

export default App;
