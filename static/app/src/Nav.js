import React, { Component } from 'react';

const Nav = ({ restart, shownDownload }) => {
  let downloadCss = "pt-button pt-icon-download pt-intent-success"
  if (!shownDownload) {
    downloadCss += " pt-disabled"
  }
  return (
    <nav className="pt-navbar pt-dark">
      <div className="pt-navbar-group pt-align-left">
        <div className="pt-navbar-heading">PV Sim</div>
        <button className="pt-button pt-minimal pt-icon-refresh" onClick={restart}>Start</button>
        <a href={shownDownload && "/files/data.csv"} className={downloadCss} role="button">Simulation Log</a>
      </div>
    </nav>
  )
}

export default Nav;
