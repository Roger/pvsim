import moment from 'moment';
import React from 'react';

const Logger = ({ data }) => (
  <table className="pt-table pt-condensed pt-striped fullwidth">
    <thead>
      <tr>
        <th>Date</th>
        <th>PV</th>
        <th>Power</th>
        <th>Total</th>
      </tr>
    </thead>
    <tbody>
      {data.map(msg => (
        <tr key={msg.time}>
          <td>{moment(msg.time).format('ll LTS')}</td>
          <td>{msg.pv.toFixed(0)}</td>
          <td>{msg.power}</td>
          <td>{msg.total.toFixed(0)}</td>
        </tr>
      ))}
    </tbody>
  </table>
)

export default Logger
