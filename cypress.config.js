const { defineConfig } = require("cypress");
const http = require("http");

// State management for stress tests (Node.js context, outside browser)
let stressTestResults = [];

module.exports = defineConfig({
  e2e: {
    baseUrl: 'http://localhost:5000/',
    setupNodeEvents(on, config) {
      on('task', {
        fetchWebpackScript() {
          return new Promise((resolve, reject) => {
            const req = http.get('http://localhost:8080/index.js', (res) => {
              if (res.statusCode !== 200) {
                reject(new Error(`HTTP ${res.statusCode}: ${res.statusMessage}`));
                return;
              }
              let data = '';
              res.on('data', chunk => data += chunk);
              res.on('end', () => resolve(data));
            }).on('error', (err) => reject(err));
            req.setTimeout(10000, () => {
              req.destroy();
              reject(new Error('Request timeout after 10s'));
            });
          });
        },
        log(message) {
          console.log(message);
          return null;
        },
        // Stress test result management
        'stressTest:addResult'(result) {
          stressTestResults.push(result);
          console.log(`Stored result for run ${result.run}: ${result.time}ms, ${result.markerCount} markers`);
          return null;
        },
        'stressTest:getResults'() {
          return stressTestResults;
        },
        'stressTest:reset'() {
          stressTestResults = [];
          console.log('Reset stress test results');
          return null;
        }
      });
      return config;
    },
}
});

