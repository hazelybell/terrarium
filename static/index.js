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
  let d = document.querySelector('#cputemp_current');
  d.innerText = o.temp + " °C";
  if (cputemp_data && cputemp_chart) {
    let data = cputemp_data.series[0].data;
    data.push({x: o.time, y: o.temp});
//         console.log(cputemp_data.series[0].data);
    let now = Date.now() / 1000;
//         console.log(data[0].x + "<" + (now - cputemp_tspan));
    while (data[0].x < now - cputemp_tspan) {
//           console.log("shifting out");
      data.shift();
    }
    cputemp_chart.update(cputemp_data);
  }
}

function lamp(o) {
  let d = document.querySelector('#lamp .boxinner');
  d.innerText = "Outlet: power " + o.power;
  d.className = "boxinner " + o.power;
}

function sm(o, n) {
  let d = document.querySelector('#sm #sm' + n);
  let v = Math.round(o.v * 100)/100;
  let min = Math.round(o.min * 100)/100;
  let max = Math.round(o.max * 100)/100;
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
  d.innerText = v + "V (" + min + "-" + max + ") " + pct + "% " + word;
  if (sm_data && sm_chart) {
    let data = sm_data.series[0].data;
    data.push({x: o.time, y: o.v});
    let now = Date.now() / 1000;
    while (data[0].x < now - sm_tspan) {
      data.shift();
    }
    sm_chart.update(sm_data);
  }
}


function handle_message(o) {
  if (o.log) {
    add_to_log(o.log);
  } else if (o.cputemp) {
    cputemp(o.cputemp);
  } else if (o.lamp) {
    lamp(o.lamp);
  } else if (o.sm1) {
    sm(o.sm1, 1);
  } else {
    console.log("Unknown state!");
  }
}

function resume_logging() {
  let ws = new WebSocket('ws://' + location.host + '/log');
  
  ws.addEventListener('message', (msg) => {
    let l = JSON.parse(msg.data);
    if (Array.isArray(l)) {
      for (let i of l) {
        handle_message(i);
      }
    } else {
      handle_message(l);
    }
  });
  
  ws.addEventListener('close', (closeEvent) => {
    resume_logging();
  });
  
  ws.addEventListener('open', (openEvent) => {
    let msg = 'refresh';
    ws.send(JSON.stringify({'viewID': viewID}));
  });
  
  return ws;
}

var cputemp_data;
var cputemp_chart;
var cputemp_tspan;

function smooth(data, selector) {
  let serieses = data.series;
  elt = document.querySelector(selector);
  width = elt.clientWidth;
  console.log("width " + width);
  for (let series of serieses) {
    let name = series.name;
    let raw = series.data;
    
  }
}

function cputemp_plot_init(tspan) {
  let ctime = Date.now() / 1000;
  let since = ctime - (tspan);
  fetch("/storage/cputemp?since=" + since).then((response) => {
    return response.json();
  }).then((json) => {
    let labels = [];
    let values = [];
    for (let r of json) {
      values.push({x: r.time, y: r.temp});
    }
    values.reverse();
    cputemp_data = {
      series: [{
        name: 'temperature',
        data: values
      }],
    };
    smooth(cputemp_data, "#cputemp .ct-chart-line");
    let config = {
      axisX: {
        type: Chartist.AutoScaleAxis,
        onlyInteger: true,
        scaleMinSpace: 100,
      },
      series: {
        'temperature': {
          showLine: true,
          lineSmooth: false,
//               lineSmooth: Chartist.Interpolation.simple({
//                 divisor: 4,
//                 fillHoles: true,
//               }),
        }
      }
    };
    if (cputemp_chart) {
      cputemp_chart.detach();
    }
    cputemp_chart = new Chartist.Line('#cputemp_ct', cputemp_data, config);
    cputemp_tspan = tspan;
  });
}

var sm_data;
var sm_chart;
var sm_tspan;

function sm_plot_init(tspan) {
  let ctime = Date.now() / 1000;
  let since = ctime - (tspan);
  fetch("/storage/sm1?since=" + since).then((response) => {
    return response.json();
  }).then((json) => {
    let labels = [];
    let values = [];
    for (let r of json) {
      values.push({x: r.time, y: r.v});
    }
    values.reverse();
    sm_data = {
      series: [{
        name: 'sm1',
        data: values
      }],
    };
    let config = {
      axisX: {
        type: Chartist.AutoScaleAxis,
        onlyInteger: true,
        scaleMinSpace: 100,
      },
      series: {
        'sm1': {
          showLine: true,
          lineSmooth: false,
        }
      }
    };
    if (sm_chart) {
      sm_chart.detach();
    }
    sm_chart = new Chartist.Line('#sm_ct', sm_data, config);
    sm_tspan = tspan;
  });
}

document.addEventListener('DOMContentLoaded', function(){
  let ws = resume_logging();

  document.getElementById("cputemp_day").addEventListener("click",
    function() {
      cputemp_plot_init(60*60*24);
    }
  );
  document.getElementById("cputemp_hour").addEventListener("click",
    function() {
      cputemp_plot_init(60*60);
    }
  );

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
