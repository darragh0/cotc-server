document.addEventListener("DOMContentLoaded", () => {
  var canvas = document.getElementById("latest__gauge__canvas");
  if (!canvas) return;

  var style = getComputedStyle(document.documentElement);
  var grey = style.getPropertyValue("--terminal-grey");
  var purple = style.getPropertyValue("--terminal-purple");
  var dimPurple = style.getPropertyValue("--terminal-dim-purple");
  var red = style.getPropertyValue("--terminal-red");

  var opts = {
    radiusScale: 1.05,
    angle: 0,
    lineWidth: 0.2,
    colorStart: purple,
    colorStop: dimPurple,
    strokeColor: grey,
    generateGradient: true,
    pointer: {
      length: 0.5,
      strokeWidth: 0.035,
      color: red
    },
  };

  var gaugeValue = parseFloat(canvas.dataset.value);
  var gauge = new Gauge(canvas).setOptions(opts);
  gauge.maxValue = 100;
  gauge.set(gaugeValue);
  gauge.text = gaugeValue;
});
