/**
 * Enhanced Charts Module - Advanced visualizations for golf data
 */

// Chart.js plugins configuration
Chart.defaults.font.family = '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif';

/**
 * Shot Dispersion Heat Map
 */
export function createShotDispersionChart(canvasId, shotData) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    
    // Process shot data into scatter points
    const scatterData = shotData.map(shot => ({
        x: shot.side_deviation_yards || shot.offline_distance_yards || 0,
        y: shot.total_distance_yards || shot.carry_distance_yards || 0,
        r: 5, // Point radius
        backgroundColor: getDispersionColor(shot),
        shot: shot // Store original shot data
    }));
    
    // Calculate averages for reference lines
    const avgDistance = shotData.reduce((sum, shot) => 
        sum + (shot.total_distance_yards || 0), 0) / shotData.length;
    
    return new Chart(ctx, {
        type: 'scatter',
        data: {
            datasets: [{
                label: 'Shot Dispersion',
                data: scatterData,
                backgroundColor: scatterData.map(d => d.backgroundColor),
                borderColor: 'rgba(0, 0, 0, 0.1)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: 'Shot Dispersion Pattern'
                },
                tooltip: {
                    callbacks: {
                        label: (context) => {
                            const shot = context.raw.shot;
                            return [
                                `Distance: ${shot.total_distance_yards || 0} yards`,
                                `Offline: ${Math.abs(shot.side_deviation_yards || 0)} yards ${shot.side_deviation_yards > 0 ? 'right' : 'left'}`,
                                `Club: ${shot.club}`,
                                shot.notes ? `Note: ${shot.notes}` : ''
                            ].filter(Boolean);
                        }
                    }
                },
                annotation: {
                    annotations: {
                        centerLine: {
                            type: 'line',
                            xMin: 0,
                            xMax: 0,
                            borderColor: 'rgb(255, 99, 132)',
                            borderWidth: 2,
                            borderDash: [5, 5],
                            label: {
                                content: 'Target Line',
                                enabled: true,
                                position: 'start'
                            }
                        },
                        avgDistance: {
                            type: 'line',
                            yMin: avgDistance,
                            yMax: avgDistance,
                            borderColor: 'rgb(54, 162, 235)',
                            borderWidth: 2,
                            borderDash: [10, 5],
                            label: {
                                content: `Avg: ${Math.round(avgDistance)} yards`,
                                enabled: true,
                                position: 'end'
                            }
                        }
                    }
                }
            },
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'Yards Offline (- Left, + Right)'
                    },
                    min: -50,
                    max: 50,
                    grid: {
                        color: (context) => context.tick.value === 0 ? '#666' : '#e0e0e0'
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: 'Total Distance (yards)'
                    },
                    min: 0
                }
            }
        }
    });
}

/**
 * Get color for dispersion point based on accuracy
 */
function getDispersionColor(shot) {
    const offline = Math.abs(shot.side_deviation_yards || 0);
    
    if (offline < 5) return 'rgba(46, 204, 113, 0.6)';  // Green - excellent
    if (offline < 10) return 'rgba(52, 152, 219, 0.6)'; // Blue - good
    if (offline < 20) return 'rgba(241, 196, 15, 0.6)'; // Yellow - average
    return 'rgba(231, 76, 60, 0.6)'; // Red - poor
}

/**
 * Club Gapping Visualization with Gap Analysis
 */
export function createClubGappingChart(canvasId, clubData) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    
    // Sort clubs by average distance
    const sortedClubs = [...clubData].sort((a, b) => 
        (b.avg_carry_distance || 0) - (a.avg_carry_distance || 0)
    );
    
    // Calculate gaps
    const gaps = [];
    for (let i = 0; i < sortedClubs.length - 1; i++) {
        const gap = (sortedClubs[i].avg_carry_distance || 0) - 
                   (sortedClubs[i + 1].avg_carry_distance || 0);
        gaps.push(gap);
    }
    
    // Create gap annotations
    const gapAnnotations = {};
    gaps.forEach((gap, index) => {
        const color = gap < 10 ? 'rgba(231, 76, 60, 0.8)' : 
                     gap > 20 ? 'rgba(241, 196, 15, 0.8)' : 
                     'rgba(46, 204, 113, 0.8)';
        
        gapAnnotations[`gap${index}`] = {
            type: 'label',
            xValue: index + 0.5,
            yValue: (sortedClubs[index].avg_carry_distance + sortedClubs[index + 1].avg_carry_distance) / 2,
            content: `${Math.round(gap)}yd`,
            backgroundColor: color,
            color: 'white',
            borderRadius: 4,
            padding: 4,
            font: {
                size: 11
            }
        };
    });
    
    return new Chart(ctx, {
        type: 'bar',
        data: {
            labels: sortedClubs.map(c => c.name),
            datasets: [{
                label: 'Carry Distance',
                data: sortedClubs.map(c => c.avg_carry_distance || 0),
                backgroundColor: 'rgba(44, 140, 88, 0.6)',
                borderColor: 'rgba(44, 140, 88, 1)',
                borderWidth: 1
            }, {
                label: 'Total Distance',
                data: sortedClubs.map(c => c.avg_total_distance || 0),
                backgroundColor: 'rgba(52, 152, 219, 0.6)',
                borderColor: 'rgba(52, 152, 219, 1)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: 'Club Distances & Gapping'
                },
                tooltip: {
                    callbacks: {
                        afterLabel: (context) => {
                            const club = sortedClubs[context.dataIndex];
                            return [
                                `Consistency: ±${club.distance_std_dev || 0} yards`,
                                `Samples: ${club.shot_count || 0}`
                            ];
                        }
                    }
                },
                annotation: {
                    annotations: gapAnnotations
                }
            },
            scales: {
                y: {
                    title: {
                        display: true,
                        text: 'Distance (yards)'
                    },
                    beginAtZero: false
                }
            }
        }
    });
}

/**
 * Strokes Gained Visualization
 */
export function createStrokesGainedChart(canvasId, strokesGainedData) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    
    // Categories and their data
    const categories = ['Off the Tee', 'Approach', 'Around Green', 'Putting'];
    const values = [
        strokesGainedData.off_tee || 0,
        strokesGainedData.approach || 0,
        strokesGainedData.around_green || 0,
        strokesGainedData.putting || 0
    ];
    
    // Color based on positive/negative
    const colors = values.map(v => v >= 0 ? 
        'rgba(46, 204, 113, 0.7)' : 'rgba(231, 76, 60, 0.7)'
    );
    
    const borderColors = values.map(v => v >= 0 ? 
        'rgba(46, 204, 113, 1)' : 'rgba(231, 76, 60, 1)'
    );
    
    return new Chart(ctx, {
        type: 'bar',
        data: {
            labels: categories,
            datasets: [{
                label: 'Strokes Gained/Lost',
                data: values,
                backgroundColor: colors,
                borderColor: borderColors,
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: `Strokes Gained vs ${strokesGainedData.benchmark || 'Scratch'}`
                },
                tooltip: {
                    callbacks: {
                        label: (context) => {
                            const value = context.parsed.y;
                            const label = value >= 0 ? 'Gained' : 'Lost';
                            return `${label}: ${Math.abs(value).toFixed(2)} strokes`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    title: {
                        display: true,
                        text: 'Strokes Gained/Lost per Round'
                    },
                    grid: {
                        color: (context) => context.tick.value === 0 ? '#666' : '#e0e0e0'
                    }
                }
            }
        }
    });
}

/**
 * Performance Trend with Multiple Metrics
 */
export function createPerformanceTrendChart(canvasId, trendData) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    
    // Define datasets with different metrics
    const datasets = [
        {
            label: 'Score',
            data: trendData.scores,
            borderColor: 'rgb(255, 99, 132)',
            backgroundColor: 'rgba(255, 99, 132, 0.1)',
            yAxisID: 'y-score',
            tension: 0.3
        },
        {
            label: 'Fairways Hit %',
            data: trendData.fairwayPct,
            borderColor: 'rgb(54, 162, 235)',
            backgroundColor: 'rgba(54, 162, 235, 0.1)',
            yAxisID: 'y-percentage',
            tension: 0.3
        },
        {
            label: 'GIR %',
            data: trendData.girPct,
            borderColor: 'rgb(75, 192, 192)',
            backgroundColor: 'rgba(75, 192, 192, 0.1)',
            yAxisID: 'y-percentage',
            tension: 0.3
        },
        {
            label: 'Putts/Round',
            data: trendData.puttsPerRound,
            borderColor: 'rgb(153, 102, 255)',
            backgroundColor: 'rgba(153, 102, 255, 0.1)',
            yAxisID: 'y-putts',
            tension: 0.3
        }
    ];
    
    return new Chart(ctx, {
        type: 'line',
        data: {
            labels: trendData.labels,
            datasets: datasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: 'index',
                intersect: false
            },
            plugins: {
                title: {
                    display: true,
                    text: 'Performance Trends'
                },
                legend: {
                    position: 'top',
                    labels: {
                        usePointStyle: true,
                        padding: 15
                    }
                }
            },
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'Date'
                    }
                },
                'y-score': {
                    type: 'linear',
                    display: true,
                    position: 'left',
                    title: {
                        display: true,
                        text: 'Score'
                    },
                    reverse: true // Lower scores are better
                },
                'y-percentage': {
                    type: 'linear',
                    display: true,
                    position: 'right',
                    title: {
                        display: true,
                        text: 'Percentage'
                    },
                    min: 0,
                    max: 100,
                    grid: {
                        drawOnChartArea: false
                    }
                },
                'y-putts': {
                    type: 'linear',
                    display: false,
                    position: 'right',
                    min: 20,
                    max: 40
                }
            }
        }
    });
}

/**
 * Practice Goal Progress Radial Chart
 */
export function createGoalProgressChart(canvasId, goalData) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    
    // Calculate progress percentage
    const progress = ((goalData.current - goalData.baseline) / 
                     (goalData.target - goalData.baseline) * 100).toFixed(1);
    
    return new Chart(ctx, {
        type: 'doughnut',
        data: {
            datasets: [{
                data: [progress, Math.max(0, 100 - progress)],
                backgroundColor: [
                    progress >= 100 ? 'rgba(46, 204, 113, 0.8)' :
                    progress >= 75 ? 'rgba(52, 152, 219, 0.8)' :
                    progress >= 50 ? 'rgba(241, 196, 15, 0.8)' :
                    'rgba(231, 76, 60, 0.8)',
                    'rgba(200, 200, 200, 0.2)'
                ],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            circumference: 180,
            rotation: 270,
            cutout: '75%',
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    enabled: false
                }
            }
        },
        plugins: [{
            id: 'goal-center-text',
            beforeDraw: (chart) => {
                const { ctx, chartArea } = chart;
                const centerX = (chartArea.left + chartArea.right) / 2;
                const centerY = (chartArea.top + chartArea.bottom) / 2 + 20;
                
                ctx.save();
                ctx.textAlign = 'center';
                ctx.textBaseline = 'middle';
                
                // Progress percentage
                ctx.font = 'bold 36px -apple-system, sans-serif';
                ctx.fillStyle = '#333';
                ctx.fillText(`${progress}%`, centerX, centerY - 15);
                
                // Goal name
                ctx.font = '14px -apple-system, sans-serif';
                ctx.fillStyle = '#666';
                ctx.fillText(goalData.name, centerX, centerY + 15);
                
                // Current vs Target
                ctx.font = '12px -apple-system, sans-serif';
                ctx.fillText(`${goalData.current} / ${goalData.target}`, centerX, centerY + 35);
                
                ctx.restore();
            }
        }]
    });
}

/**
 * Shot Pattern Radar Chart
 */
export function createShotPatternRadar(canvasId, patternData) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    
    return new Chart(ctx, {
        type: 'radar',
        data: {
            labels: ['Straight', 'Draw', 'Fade', 'Pull', 'Push', 'Hook', 'Slice'],
            datasets: [{
                label: 'Shot Pattern Distribution',
                data: [
                    patternData.straight || 0,
                    patternData.draw || 0,
                    patternData.fade || 0,
                    patternData.pull || 0,
                    patternData.push || 0,
                    patternData.hook || 0,
                    patternData.slice || 0
                ],
                backgroundColor: 'rgba(52, 152, 219, 0.2)',
                borderColor: 'rgba(52, 152, 219, 1)',
                pointBackgroundColor: 'rgba(52, 152, 219, 1)',
                pointBorderColor: '#fff',
                pointHoverBackgroundColor: '#fff',
                pointHoverBorderColor: 'rgba(52, 152, 219, 1)'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: 'Shot Pattern Distribution'
                },
                legend: {
                    display: false
                }
            },
            scales: {
                r: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 10
                    },
                    pointLabels: {
                        font: {
                            size: 12
                        }
                    }
                }
            }
        }
    });
}

/**
 * Weather Impact Analysis Chart
 */
export function createWeatherImpactChart(canvasId, weatherData) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    
    // Group data by temperature ranges
    const tempRanges = ['< 50°F', '50-60°F', '60-70°F', '70-80°F', '80-90°F', '> 90°F'];
    const avgDistances = weatherData.map(range => range.avgDistance);
    const sampleSizes = weatherData.map(range => range.sampleSize);
    
    return new Chart(ctx, {
        type: 'line',
        data: {
            labels: tempRanges,
            datasets: [{
                label: 'Average Distance',
                data: avgDistances,
                borderColor: 'rgb(255, 99, 132)',
                backgroundColor: 'rgba(255, 99, 132, 0.1)',
                yAxisID: 'y-distance',
                tension: 0.3
            }, {
                label: 'Sample Size',
                data: sampleSizes,
                type: 'bar',
                backgroundColor: 'rgba(54, 162, 235, 0.3)',
                borderColor: 'rgba(54, 162, 235, 1)',
                borderWidth: 1,
                yAxisID: 'y-samples'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: 'Temperature Impact on Distance'
                }
            },
            scales: {
                'y-distance': {
                    type: 'linear',
                    display: true,
                    position: 'left',
                    title: {
                        display: true,
                        text: 'Average Distance (yards)'
                    }
                },
                'y-samples': {
                    type: 'linear',
                    display: true,
                    position: 'right',
                    title: {
                        display: true,
                        text: 'Number of Shots'
                    },
                    grid: {
                        drawOnChartArea: false
                    }
                }
            }
        }
    });
}

/**
 * Handicap Progress Chart with Trend Line
 */
export function createHandicapProgressChart(canvasId, handicapData) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    
    // Calculate trend line
    const trendLine = calculateTrendLine(handicapData.values);
    
    return new Chart(ctx, {
        type: 'line',
        data: {
            labels: handicapData.dates,
            datasets: [{
                label: 'Handicap Index',
                data: handicapData.values,
                borderColor: 'rgb(255, 99, 132)',
                backgroundColor: 'rgba(255, 99, 132, 0.1)',
                tension: 0.1,
                pointRadius: 4,
                pointHoverRadius: 6
            }, {
                label: 'Trend',
                data: trendLine,
                borderColor: 'rgba(54, 162, 235, 0.8)',
                borderDash: [5, 5],
                pointRadius: 0,
                fill: false
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: 'Handicap Progress'
                },
                annotation: {
                    annotations: {
                        goal: {
                            type: 'line',
                            yMin: handicapData.goal,
                            yMax: handicapData.goal,
                            borderColor: 'rgba(46, 204, 113, 0.8)',
                            borderWidth: 2,
                            borderDash: [10, 5],
                            label: {
                                content: `Goal: ${handicapData.goal}`,
                                enabled: true,
                                position: 'end'
                            }
                        }
                    }
                }
            },
            scales: {
                y: {
                    title: {
                        display: true,
                        text: 'Handicap Index'
                    },
                    reverse: true // Lower is better
                }
            }
        }
    });
}

/**
 * Calculate linear trend line
 */
function calculateTrendLine(values) {
    const n = values.length;
    const x = Array.from({ length: n }, (_, i) => i);
    
    const sumX = x.reduce((a, b) => a + b, 0);
    const sumY = values.reduce((a, b) => a + b, 0);
    const sumXY = x.reduce((total, xi, i) => total + xi * values[i], 0);
    const sumX2 = x.reduce((total, xi) => total + xi * xi, 0);
    
    const slope = (n * sumXY - sumX * sumY) / (n * sumX2 - sumX * sumX);
    const intercept = (sumY - slope * sumX) / n;
    
    return x.map(xi => slope * xi + intercept);
}

/**
 * Export chart as image
 */
export function exportChartAsImage(chart, filename = 'chart.png') {
    const link = document.createElement('a');
    link.download = filename;
    link.href = chart.toBase64Image();
    link.click();
}

/**
 * Destroy all charts in a container
 */
export function destroyChartsInContainer(containerId) {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    const canvases = container.querySelectorAll('canvas');
    canvases.forEach(canvas => {
        const chart = Chart.getChart(canvas);
        if (chart) {
            chart.destroy();
        }
    });
}