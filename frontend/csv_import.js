/**
 * CSV Import functionality for GolfStats frontend
 */

/**
 * Import CSV file to a range session
 * @param {number} sessionId - The range session ID
 * @param {File} file - The CSV file to import
 * @param {string|null} sourceSystem - Optional source system override (e.g., 'trackman', 'skytrak')
 * @param {string} shotType - Shot type (default: 'range')
 * @returns {Promise<Object>} - Promise resolving to the import results
 */
async function importCsvToRangeSession(sessionId, file, sourceSystem = null, shotType = 'range') {
    // Validate input
    if (!sessionId) {
        throw new Error('Session ID is required');
    }
    
    if (!file || !(file instanceof File)) {
        throw new Error('Valid CSV file is required');
    }
    
    // Validate file type
    if (!file.name.toLowerCase().endsWith('.csv')) {
        throw new Error('File must be a CSV document');
    }
    
    // Create form data
    const formData = new FormData();
    formData.append('file', file);
    
    // Add optional parameters if provided
    if (sourceSystem) {
        formData.append('source_system', sourceSystem);
    }
    
    if (shotType) {
        formData.append('shot_type', shotType);
    }
    
    try {
        // Send request to API
        const response = await fetch(`/api/range-sessions/${sessionId}/import-csv`, {
            method: 'POST',
            body: formData,
            // No content-type header needed, it's set automatically with FormData
        });
        
        // Parse response
        const result = await response.json();
        
        // Check for errors
        if (!response.ok) {
            throw new Error(result.error || 'Failed to import CSV');
        }
        
        return result;
    } catch (error) {
        console.error('CSV import error:', error);
        throw error;
    }
}

/**
 * Preview CSV content before import (shows a sample of mapped data)
 * @param {File} file - The CSV file to preview
 * @returns {Promise<Object>} - Promise resolving to the preview data
 */
async function previewCsvFile(file) {
    return new Promise((resolve, reject) => {
        if (!file || !(file instanceof File)) {
            reject(new Error('Valid CSV file is required'));
            return;
        }
        
        const reader = new FileReader();
        
        reader.onload = function(event) {
            try {
                const csvContent = event.target.result;
                const lines = csvContent.split('\n');
                
                // Need at least a header row and one data row
                if (lines.length < 2) {
                    reject(new Error('CSV file must contain a header row and at least one data row'));
                    return;
                }
                
                // Parse header row
                const headers = parseCSVLine(lines[0]);
                
                // Parse a sample of data rows (up to 5)
                const sampleRows = [];
                const maxSampleRows = Math.min(5, lines.length - 1);
                
                for (let i = 1; i <= maxSampleRows; i++) {
                    if (lines[i].trim()) { // Skip empty lines
                        const rowData = parseCSVLine(lines[i]);
                        const row = {};
                        
                        // Map each value to its header
                        headers.forEach((header, index) => {
                            if (index < rowData.length) {
                                row[header] = rowData[index];
                            }
                        });
                        
                        sampleRows.push(row);
                    }
                }
                
                resolve({
                    headers: headers,
                    sampleRows: sampleRows,
                    totalRows: lines.filter(line => line.trim()).length - 1 // Exclude header row
                });
            } catch (error) {
                reject(error);
            }
        };
        
        reader.onerror = function() {
            reject(new Error('Error reading CSV file'));
        };
        
        reader.readAsText(file);
    });
}

/**
 * Parse a CSV line into an array of values
 * Handles quoted values and commas within quotes
 * @param {string} line - The CSV line to parse
 * @returns {Array<string>} - Array of values
 */
function parseCSVLine(line) {
    const values = [];
    let currentValue = '';
    let inQuotes = false;
    
    for (let i = 0; i < line.length; i++) {
        const char = line[i];
        
        if (char === '"' && (i === 0 || line[i-1] !== '\\')) {
            // Toggle quote state if not escaped
            inQuotes = !inQuotes;
        } else if (char === ',' && !inQuotes) {
            // End of field if comma outside quotes
            values.push(currentValue.trim());
            currentValue = '';
        } else {
            // Add character to current field
            currentValue += char;
        }
    }
    
    // Add the last field
    values.push(currentValue.trim());
    
    return values;
}

// Export functions
window.GolfStats = window.GolfStats || {};
window.GolfStats.CSVImport = {
    importCsvToRangeSession,
    previewCsvFile
};