function toUpperCaseNoWhitespace(input) {
    // Convert the input value to uppercase and remove whitespaces
    input.value = input.value.toUpperCase().replace(/\s/g, '');
}


function toTitleCase(input) {
    // Get the value of the input and ensure it's a string
    let value = input.value || ''; // Fallback to an empty string if value is undefined or null

    // Title case the string
    value = value.replace(/\w\S*/g, function(word) {
        return word.charAt(0).toUpperCase() + word.substr(1).toLowerCase();
    });

    // Update the value with the title-cased text, ensuring it doesn't exceed maxlength
    input.value = value.slice(0, input.maxLength);
}

function toTitleCase(input) {
    let value = input.value || ''; // Ensure it's a string
    // Use a delay to prevent conflict with continuous typing
    value = value.replace(/\w\S*/g, function(word) {
        return word.charAt(0).toUpperCase() + word.substr(1).toLowerCase();
    });
    input.value = value;
}



function toSentenceCase(input) {
    let value = input.value || ''; // Ensure it's a string
    value = value.charAt(0).toUpperCase() + value.slice(1).toLowerCase(); // Capitalize first letter of the sentence
    input.value = value.slice(0, input.maxLength); // Ensure maxlength is respected
}


function toLowerCase(input) {
    let value = input.value || ''; // Ensure it's a string
    value = value.toLowerCase();
    input.value = value.slice(0, input.maxLength); // Ensure maxlength is respected
}


function validateNumberInput(input) {
    // Only allow digits 0-9
    input.value = input.value.replace(/[^0-9]/g, '');

    // Optionally, limit the number of characters
    if (input.value.length > 4) {  // For example, limit to 4 digits
        input.value = input.value.slice(0, 4);
    }
}


const sanitizeZipCode = (inputElement) => {
    // Replace all non-numeric characters with an empty string
    inputElement.value = inputElement.value.replace(/\D/g, '');

    // Optionally, limit the length to 6 characters (if you want to restrict the length)
    if (inputElement.value.length > 6) {
        inputElement.value = inputElement.value.slice(0, 6);
    }
};
