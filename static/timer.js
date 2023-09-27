$(document).ready(function() {
    var running = false;
    var inspectionRunning = false;
    var inspectionStartTime;
    var interval;
    var inspectionInterval;
    var spaceCount = 0;
    var spacePressed = false;

    updateTimerData();

    function formatTime(elapsedTime) {
        var minutes = Math.floor(elapsedTime / 60000);
        var seconds = Math.floor((elapsedTime % 60000) / 1000);
        var milliseconds = Math.floor((elapsedTime % 1000) / 10);

        if (minutes > 0) {
            return (minutes < 10 ? "0" : "") + minutes + "." +
                (seconds < 10 ? "0" : "") + seconds + "." +
                (milliseconds < 10 ? "0" : "") + milliseconds;
        } else {
            return (seconds < 10 ? "0" : "") + seconds + "." +
                (milliseconds < 10 ? "0" : "") + milliseconds;
        }
    }

    function startInspection() {
        document.getElementById('scramble').style.display = 'none';
        document.getElementById('score').style.display = 'none';
        document.getElementById('btn_timer').style.display = 'none';

        inspectionStartTime = new Date().getTime();
        inspectionInterval = setInterval(function() {
            var currentTime = new Date().getTime();
            var elapsedTime = currentTime - inspectionStartTime;
            var remainingTime = 15000 - elapsedTime; // 15 seconds - elapsed time
            if (remainingTime <= 0) {
                clearInterval(inspectionInterval);
                startTimer();
                inspectionRunning = false;
            } else {
                $("#timer").text(Math.ceil(remainingTime / 1000));
            }
        }, 10);
        inspectionRunning = true;
    }

    function startTimer() {
        startTime = new Date().getTime();
        interval = setInterval(function() {
            var currentTime = new Date().getTime();
            var elapsedTime = currentTime - startTime;
            $("#timer").text(formatTime(elapsedTime));
        }, 10);
        running = true;
    }

    function updateTimerData() {
    // Отправка асинхронного запроса на сервер для обновления данных AO5 и AO10
    $.ajax({
        url: "/get_ao_data",
        type: "GET",
        success: function(response) {
            // Обновление данных AO5 и AO10 на странице
            $("#ao5").text(response.ao5);
            $("#ao10").text(response.ao10);
            $("#ao100").text(response.ao100);
            $("#mean").text(response.mean)
        },
        error: function(xhr, status, error) {
            console.error("Ошибка получения данных AO5 и AO10:", error);
        }
    });
    }

    function stopTimer() {
        document.getElementById('scramble').style.display = 'block';
        document.getElementById('score').style.display = 'block';
        document.getElementById('btn_timer').style.display = 'block';


        clearInterval(interval);
        running = false;

        // Получение времени после остановки таймера и отправка на сервер
        var currentTime = new Date().getTime();
        var elapsedTime = currentTime - startTime;
        var currentScramble = $("#scramble").text();

        $.post("/stop_timer", { time: elapsedTime, scramble: currentScramble }, function(response) {
            console.log("Timer stopped. Time sent to server:", elapsedTime);
        });

        // Обновление значения скрамбла на странице
        $.ajax({
            url: "/generate_scramble",
            type: "GET",
            success: function(response) {
                console.log("Scramble Updated:", response);
                $("#scramble").text(response);
            },
            error: function(xhr, status, error) {
                console.error("Ошибка получения скрамбла:", error);
            }
        });

        updateTimerData();
    }


    $(document).keydown(function(event) {
        if (event.keyCode === 32) { // Код клавиши пробела
            event.preventDefault(); // Предотвращаем прокрутку страницы при нажатии пробела
            if (!spacePressed) { // Если клавиша пробела не удерживается
                spacePressed = true; // Устанавливаем флаг в состояние удержания
                if (inspectionRunning) {
                    // Если инспекция идет, первое нажатие пробела останавливает инспекцию и запускает таймер
                    clearInterval(inspectionInterval);
                    startTimer();
                    inspectionRunning = false;
                } else {
                    if (running) {
                        // Если таймер идет, второе нажатие пробела останавливает таймер
                        stopTimer();
                    } else {
                        // Третье нажатие пробела запускает инспекцию
                        startInspection();
                    }
                }
            }
        }
    });

    $(document).keyup(function(event) {
        if (event.keyCode === 32) { // Код клавиши пробела
            spacePressed = false; // Устанавливаем флаг в состояние отпускания
        }
    });
});
