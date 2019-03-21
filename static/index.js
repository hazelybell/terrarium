'use strict';

function uuidv4() { /* https://stackoverflow.com/a/2117523 2019-03-14 */
  return ([1e7]+-1e3+-4e3+-8e3+-1e11).replace(/[018]/g, c =>
    (c ^ crypto.getRandomValues(new Uint8Array(1))[0] & 15 >> c / 4).toString(16)
  )
}    
var viewID = uuidv4();

console.log(viewID);

function add_to_log(l) {
  let p = document.createElement('tr');
  
  let lev = document.createElement('td');
  lev.className = "level";
  lev.innerText = l.level;
  p.appendChild(lev);
  
  let t = document.createElement('td');
  t.className = "time";
  t.innerText = l.time;
  p.appendChild(t);
  
  let mod = document.createElement('td');
  mod.className = "module";
  mod.innerText = l.module;
  p.appendChild(mod);
  
  let m = document.createElement('td');
  m.className = "msg";
  m.innerText = l.msg;
  p.appendChild(m);
  
  p.className = l.level + " " + l.module;
  var logDiv = document.getElementById('logbody')
  logDiv.appendChild(p);
  var pOffset = p.offsetTop;
  document.getElementById('loginner').scrollTop = pOffset;
}

function cputemp(o) {
}

function lamp(o) {
  let d = document.querySelector('#lamp .boxinner');
  d.innerText = "Outlet: power " + o.power;
  d.className = "boxinner " + o.power;
}

function sm(o, n) {
  let d = document.querySelector('#sm #sm' + n);
  let v = Math.round(o.v * 100)/100;
  let pct = Math.round(o.pct * 10)/10;
  let word;
  if (pct > 66.6) {
    word = "water";
  } else if (pct < 33.3) {
    word = "dry";
  } else {
    word = "wet";
  }
  d.className = word;
  d.innerText = v + "V " + pct + "% " + word;
  if (sm_data && sm_chart) {
    let data = sm_data.series[n-1].data;
    data.push({x: o.time, y: o.pct});
    let now = Date.now() / 1000;
    while (data[0].x < now - sm_tspan) {
      data.shift();
    }
    let smoothed = smooth(sm_data, '#sm_ct');
    sm_chart.update(smoothed);
  }
}

class RemoteObserver {
  setState(state) {
    throw new Error("Not implemented");
  }
  
//   updateState(state) {
//     this.set_state(state);
//     if (this.now_has_state) {
//       this.now_has_state();
//       this.now_has_state = false;
//     }
//   }
  
  connect() {
    this.ws = new WebSocket("ws://" + location.host + '/' + this.path);
    
    this.ws.addEventListener('open', (openEvent) => {
      this.ws.send(JSON.stringify({'refresh': viewID}));
    });
    
    this.ws.addEventListener('close', (closeEvent) => {
      this.connect();
    });
    
    this.ws.addEventListener('message', (msg) => {
      let new_state = JSON.parse(msg.data);
      this.setState(new_state);
    });
  }
  
  constructor(path) {
    this.path = path;
    this.has_state = new Promise((resolve, reject) => {
      this.now_has_state = resolve;
    });
    this.connect();
  }
}

let observableMixin = Base => class extends Base {
  constructor() {
    super(...arguments);
    this.observers = [];
  }
  
  getState() {
    return this.state;
  }
  
  setState(new_state) {
    this.state = new_state;
    this.notify_all();
  }
  
  observe(observer, key) {
    this.observers.push([observer, key]);
  }
  
  notify_all() {
    let state = this.getState();
    for (let observerKey of this.observers) {
      let observer = observerKey[0];
      let key = observerKey[1];
      observer.notify(state, key);
    }
  }
}

class RemoteObservable extends observableMixin(RemoteObserver) {
}

class Remotes {
  constructor() {
    this.log = new RemoteObservable("observables/log");
    this.cputemp = new RemoteObservable("observables/cputemp");
    this.sm = [
      new RemoteObservable("observables/sm1"),
      new RemoteObservable("observables/sm2")
    ]
  }
}

let remotes = new Remotes;

class CPUTemp {
  constructor() {
    remotes.cputemp.observe(this);
    
  }
  
  notify(state) {
    console.log(state);
    let d = document.querySelector('#cputemp_current');
    d.innerText = state.temp + " °C";
  }
}

class Plot {
  constructor(name) {
    this.name = name;
    this.chart = null;
    this.tspan = null;
    this.data = null;
    this.chart_id = "#" + this.name + "_ct";
    
    document.getElementById(this.name + "_day").addEventListener("click",
      () => {
        this.plot_init(60*60*24);
      }
    );
    document.getElementById(this.name + "_hour").addEventListener("click",
      () => {
        this.plot_init(60*60);
      }
    );
  }
  
  unplot() {
    if (this.chart) {
      this.chart.detach();
    }
    this.chart = null;
  }
  
  plot() {
    this.unplot();
    let labels = [];
    let values = [];
    this.data = {
      series: [],
    };
    let config = {
      axisX: {
        type: Chartist.AutoScaleAxis,
        onlyInteger: true,
        scaleMinSpace: 100,
      },
      series: {
      }
    };
    let n = 0;
    for (let series of this.rawData) {
      let series_name = 'plot' + (++n);
      for (let r of series) {
        values.push({x: r.time, y: r.temp});
      }
      values.reverse();
      this.data.series.push({
        name: series_name,
        data: values
      });
      config.series[series_name] = {
          showLine: true,
          showPoint: false,
          lineSmooth: false,
        }
    }
    let smoothed = smooth(this.data, this.chart_id);
    this.chart = new Chartist.Line(this.chart_id, smoothed, config);
  }
  
  plot_init(seconds) {
    let ctime = Date.now() / 1000;
    let since = ctime - seconds;
    this.tspan = seconds;
    let promises = [];
    for (let path of this.paths) {
      promises.push(
        fetch("/storage/" + this.name + "?since=" + since).then((response) => {
          return response.json();
        })
      );
    }
    Promise.all(promises).then((jsons) => {
      this.rawData = jsons;
      this.plot();
    });
  }

  notify(state, key) {
    if (this.data) {
      let data = this.data.series[key].data;
      data.push({x: state.time, y: state.temp});
      let now = Date.now() / 1000;
      while (data[0].x < now - this.tspan) {
        data.shift();
      }
    }
    if (this.chart) {
      let smoothed = smooth(this.data, this.chart_id);
      this.chart.update(smoothed);
    }
  }
}

class CPUTempPlot extends Plot {
  constructor() {
    this.paths = ["cputemp"];
    super("cputemp");
    remotes.cputemp.observe(this, 0);
  }
}

function smooth(data, selector) {
  let serieses = data.series;
  let elt = document.querySelector(selector);
  let width = elt.clientWidth;
  let goal = (width - 200) / 5; // TODO: get actual width of inner plot
//   console.log("goal " + goal);
  
  let new_data = {};
  Object.assign(new_data, data);
  let new_serieses = [];
  
  for (let series of serieses) {
    let raw = series.data;
    let name = series.name;
    let x_min = Infinity;
    let x_max = -Infinity;
    if (raw.length === 0) {
      return data;
    }
    for (let i of raw) {
      let x = i.x;
      if (x < x_min) {
        x_min = x;
      }
      if (x > x_max) {
        x_max = x;
      }
    }
    let x_width = x_max - x_min;
    let every = x_width / goal;
    console.log(
      "xmin: " + x_min + " x_max: " + x_max + "every: " + every);
    let smoothed = [];
    let maxed = [];
    let mined = [];
    function point(center_i) {
      let center_x = raw[center_i].x;
      let center_y = raw[center_i].y;
      let count = 0;
      let x_acc = 0;
      let y_acc = 0;
      let y_min = center_y;
      let y_max = center_y;
      for (
        let j = center_i-1; // start at the point before the center
        (j - 1 > 0) && (center_x - raw[j-1].x < every);
        j--
      ) { // left side
        let weight = raw[j].x - raw[j-1].x;
        x_acc = x_acc + (raw[j].x * weight);
        y_acc = y_acc + (raw[j].y * weight);
        if (raw[j].y > y_max) {
          y_max = raw[j].y;
        }
        if (raw[j].y < y_min) {
          y_min = raw[j].y;
        }
        count += weight;
      }
      for (
        let j = center_i;
        (j < raw.length) && (raw[j].x - center_x < every);
        j++
      ) { // right side
        let weight;
        if (j-1 >= 0) {
          weight = raw[j].x - raw[j-1].x;
        } else {
          weight = 1;
        }
        x_acc = x_acc + (raw[j].x * weight);
        y_acc = y_acc + (raw[j].y * weight);
        if (raw[j].y > y_max) {
          y_max = raw[j].y;
        }
        if (raw[j].y < y_min) {
          y_min = raw[j].y;
        }
        count += weight;
      }
      // emit point
      smoothed.push({
        x: center_x,
        y: y_acc / count,
      });
      maxed.push({
        x: center_x,
        y: y_max,
      });
      mined.push({
        x: center_x,
        y: y_min,
      });
    }
    let prev_x = 0;
    for (let i = 0; i < raw.length; i++) {
      if (raw[i].x - prev_x > every) {
        point(i);
        prev_x = raw[i].x;
      }
    }
//     console.log("new length: " + smoothed.length);
    let new_series = {};
    Object.assign(new_series, series);
    new_series.data = smoothed;
    new_serieses.push(new_series);
    let max_series = {};
    Object.assign(max_series, series);
    max_series.data = maxed;
    new_serieses.push(max_series);
    let min_series = {};
    Object.assign(min_series, series);
    min_series.data = mined;
    new_serieses.push(min_series);
  }
  new_data.series = new_serieses;
  return new_data;
}

document.addEventListener('DOMContentLoaded', function() {
  let cputemp = new CPUTemp();
  let cputempplot = new CPUTempPlot();
  
  document.getElementById("sm_day").addEventListener("click",
    function() {
      sm_plot_init(60*60*24);
    }
  );
  document.getElementById("sm_hour").addEventListener("click",
    function() {
      sm_plot_init(60*60);
    }
  );
}, false);
