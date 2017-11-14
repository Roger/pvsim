import moment from 'moment';
import React, { Component } from 'react';

import { ComposedChart, CartesianGrid, XAxis, YAxis, Tooltip, Legend, Line } from 'recharts';


const tooltipDateFormat = date => moment(date).format('ll LTS')

const CustomizedAxisTick = ({ x, y, stroke, payload }) => (
  <g transform={`translate(${x},${y})`}>
    <text x={0} y={-13} dy={16} textAnchor="end" fill="#666" transform="rotate(-90)" fontSize={11}>
      {moment(payload.value).format('LTS')}
    </text>
  </g>
);


export default class Chart extends React.Component {
  shouldComponentUpdate({ data, simulationEnded }) {
    return this.props.simulationEnded !== simulationEnded || data.length !== this.props.data.length
  }

  render() {
    const { data, simulationEnded } = this.props
    return(
      <ComposedChart width={900} height={400} data={data}
        margin={{ top: 5, right: 80, left: 20, bottom: 80 }}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="time" interval={10} tick={<CustomizedAxisTick />} />
        <YAxis />
        <Legend verticalAlign="top" height={36} />
        <Line dataKey="pv" stroke="#33aa33" />
        <Line dataKey="power" stroke="#aa3333" />
        <Line dataKey='total' stroke='#0077ff' />
        {simulationEnded &&
          <Tooltip
            animationDurationNumber={0}
            isAnimationActive={false}
            formatter={(data, key) => parseInt(data, 10)}
            labelFormatter={tooltipDateFormat}
          />
        }
      </ComposedChart>
    )
  }
}
