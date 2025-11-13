describe("Stress test", () => {
  const numRuns = 5;
  const minExpectedMarkers = 10; // Minimum markers that should be visible in initial viewport
  const maxAllowedTime = 20000; // 20 seconds for 100k points with lazy loading
  const runTimes = [];

  // Generate 5 separate test iterations
  for (let runIndex = 0; runIndex < numRuns; runIndex++) {
    it(`Performance run ${runIndex + 1}/${numRuns}`, function () {
      // Intercept API call to track when locations are loaded
      cy.intercept('GET', '/api/locations*').as('loadLocations');

      cy.visit('/');

      cy.window().then((win) => {
        const startTime = win.performance.now();

        // Wait for map container to be ready
        cy.get('#map', { timeout: 60000 }).should('be.visible');

        // Wait for locations API call to complete
        cy.wait('@loadLocations', { timeout: 60000 });

        // Wait for markers to stabilize (stop increasing in count)
        // This ensures all initial markers are rendered
        let previousCount = 0;
        cy.waitUntil(
          () => {
            return cy.document().then((doc) => {
              const markers = doc.querySelectorAll('.leaflet-marker-icon, .leaflet-marker-cluster');
              const currentCount = markers.length;

              // Log for debugging
              if (currentCount !== previousCount) {
                cy.log(`Marker count changed: ${previousCount} -> ${currentCount}`);
              }

              // Check if count has stabilized AND meets minimum requirement
              const isStable = currentCount === previousCount && currentCount >= minExpectedMarkers;

              previousCount = currentCount;
              return isStable;
            });
          },
          {
            timeout: 60000,
            interval: 500,
            errorMsg: `Markers did not stabilize at minimum ${minExpectedMarkers} within timeout`
          }
        ).then(() => {
          cy.get('.leaflet-marker-icon, .leaflet-marker-cluster').then((markers) => {
            cy.window().then((win) => {
              const endTime = win.performance.now();
              const runTime = endTime - startTime;
              const markerCount = markers.length;

              cy.log(`Run ${runIndex + 1} took ${runTime}ms and loaded ${markerCount} markers/clusters`);

              // Store in shared array
              runTimes.push({
                time: runTime,
                markerCount: markerCount
              });

              // Verify minimum number of markers are loaded
              expect(markerCount).to.be.greaterThan(minExpectedMarkers,
                `Expected more than ${minExpectedMarkers} markers but got ${markerCount}`);
            });
          });
        });
      });
    });
  }

  // Aggregate and save results after all tests complete
  after(() => {
    if (runTimes.length > 0) {
      // Calculate stats
      const times = runTimes.map(r => r.time);
      const avgTime = times.reduce((a, b) => a + b, 0) / times.length;
      const minTime = Math.min(...times);
      const maxTime = Math.max(...times);
      const avgMarkers = runTimes.reduce((a, b) => a + b.markerCount, 0) / runTimes.length;

      // Write performance metrics to file for PR comment
      const perfData = {
        numRuns: runTimes.length,
        expectedRuns: numRuns,
        runTimes: runTimes.map((r, i) => ({
          run: i + 1,
          time: Math.round(r.time),
          markers: r.markerCount
        })),
        avgTime: Math.round(avgTime),
        minTime: Math.round(minTime),
        maxTime: Math.round(maxTime),
        avgMarkers: Math.round(avgMarkers),
        maxAllowed: maxAllowedTime,
        passed: maxTime < maxAllowedTime && runTimes.length === numRuns
      };

      cy.writeFile('cypress/results/stress-test-perf.json', perfData);
      cy.log(`Performance data saved - Avg: ${Math.round(avgTime)}ms, Max: ${Math.round(maxTime)}ms, Avg Markers: ${Math.round(avgMarkers)}`);
    } else {
      // No runs completed - write failure data
      const perfData = {
        numRuns: 0,
        expectedRuns: numRuns,
        runTimes: [],
        avgTime: 0,
        minTime: 0,
        maxTime: 0,
        avgMarkers: 0,
        maxAllowed: maxAllowedTime,
        passed: false,
        error: 'No test runs completed'
      };
      cy.writeFile('cypress/results/stress-test-perf.json', perfData);
    }

    // Final assertions on aggregated data
    expect(runTimes.length).to.equal(numRuns, `Expected ${numRuns} runs but only ${runTimes.length} completed`);

    if (runTimes.length > 0) {
      const maxTime = Math.max(...runTimes.map(r => r.time));
      expect(maxTime).to.be.lessThan(maxAllowedTime, `The slowest run (${Math.round(maxTime)}ms) should be below ${maxAllowedTime}ms`);
    }
  });
});
