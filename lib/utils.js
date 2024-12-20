export function getRandomNumber() {
    const min = 40;
    const max = 90;
    const randomNum = Math.random() * (max - min) + min;
    return parseFloat(randomNum.toFixed(5));
}

export function sleep(time) {
    return new Promise(resolve => setTimeout(resolve, time));
}