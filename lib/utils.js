export function convertToJsonObject(str) {
    // First, remove any escaped backslashes
    const cleanedStr = str.replace(/\\/g, '');

    // Then, parse the cleaned string into a JSON object
    return JSON.parse(cleanedStr);
}
