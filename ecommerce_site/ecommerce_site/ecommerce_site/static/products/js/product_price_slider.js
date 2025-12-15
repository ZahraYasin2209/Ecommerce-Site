const min_display_price = document.getElementById("min-price-display");
const max_display_price = document.getElementById("max-price-display");
const max_display_slider = document.getElementById("max-price-slider");
const min_hidden_display = document.getElementById("min-price-hidden");
const max_hidden_display = document.getElementById("max-price-hidden");

const ABS_MIN_PRICE = 900;
const ABS_MAX_PRICE = 75000;

min_hidden_display.value = String(ABS_MIN_PRICE);

function formatCurrency(value) {
    return "PKR" + new Intl.NumberFormat("en-IN").format(value);
}

function updateMaxPrice(maxVal) {
    let max_price = parseInt(maxVal);
    const min_price = parseInt(min_hidden_display.value);

    if (max_price < min_price) {
        max_price = min_price;
        max_display_slider.value = min_price;
    }

    max_display_price.textContent = formatCurrency(max_price);
    max_hidden_display.value = max_price;

    const percentage = ((max_price - ABS_MIN_PRICE) / (ABS_MAX_PRICE - ABS_MIN_PRICE)) * 100;
    max_display_slider.style.setProperty("--value-percent", percentage + "%");
}

document.addEventListener("DOMContentLoaded", () => {
    min_display_price.textContent = formatCurrency(min_hidden_display.value);
    updateMaxPrice(max_display_slider.value);
});
