var system = require('system');

if (system.args.length === 1) {
  console.log('Usage: phantom-agent.js <some URL>');
  phantom.exit();
}

var OK_STATUSES = [
  200,
  304,
  301,
  302
];

var go = function (address) {
  var page = require('webpage').create();
  var results = {
    address: address,
    renderTime: null,
    outLinks: [],
    serverErrors: [],
    errors: [] // should be a list of objects
  };

  var startTime = 0;

  var createError = function(resource, msg, trace) {
    var error = {};
    var msgStack = [];
    if (trace) {
      msgStack.push('TRACE:');
      trace.forEach(function (t) {
        msgStack.push(' -> ' + t.file + ':' + t.line + (t.function ? ' (in function "' + t.function +'")' : ''));
      });
    }
    error.resource = resource;
    error.message = msg;
    error.trace = msgStack.join('\n');
    return error;
  };

  page.onError = function (msg, trace) {
    results.errors.push(createError("", msg, trace));
  };

  page.onResourceReceived = function(resource) {
    if (resource.status !== null && OK_STATUSES.indexOf(resource.status) === -1) {
      results.serverErrors.push({url: resource.url, status: resource.status});
    }
  };

  page.onLoadStarted = function () {
    startTime = Date.now();
  };

  page.onLoadFinished =  function (status) {
    var finishTime = Date.now();
    if (status !== 'success') {
      results.status = status;
    }
    gatherOutgoingLinks();
    results.renderTime = finishTime - startTime;
    exit();
  };

  var gatherOutgoingLinks = function () {
    results.outLinks = page.evaluate(function () {
      var res = [];
      var els = document.getElementsByTagName('a');
      for (var i = 0; i < els.length; ++i) {
        res.push(els[i].href);
      }
      return res;
    });
  };

  var exit = function () {
    console.log(JSON.stringify(results));
    phantom.exit();
  };

  page.open(address);


};

var address = system.args[1];
go(address);
