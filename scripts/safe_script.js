// ==UserScript==
// @name         YouTube x4 Speed Button Dummy
// @namespace    http://tampermonkey.net
// @version      1.0
// @description  Adds a dummy x4 speed button near the YouTube logo for testing purposes.
// @author       You
// @match        https://youtube.com*
// @grant        none
// ==/UserScript==

(function() {
    'use strict';

    // Функция для создания и добавления кнопки
    function injectButton() {
        // Проверяем, не была ли кнопка уже добавлена
        if (document.getElementById('yt-x4-test-btn')) return;

        // Ищем контейнер логотипа YouTube (стандартный селектор для ПК версии)
        const logoContainer = document.querySelector('ytd-topbar-logo-renderer');

        if (logoContainer) {
            // Создаем элемент кнопки
            const btn = document.createElement('button');
            btn.id = 'yt-x4-test-btn';
            btn.innerText = 'x4';

            // Минимальные inline-стили, чтобы она не ломала верстку, но была заметна
            btn.style.marginLeft = '15px';
            btn.style.padding = '5px 10px';
            btn.style.cursor = 'pointer';

            // Простейшее безопасное действие при клике
            btn.addEventListener('click', () => {
                alert('Интерфейс работает! Кнопка x4 была нажата.');
            });

            // Добавляем кнопку сразу после логотипа
            logoContainer.parentNode.insertBefore(btn, logoContainer.nextSibling);
            console.log('🥭 [Test Script] Кнопка x4 успешно добавлена поверх интерфейса YouTube.');
        }
    }

    // Поскольку YouTube является Single Page Application (SPA), используем MutationObserver
    // для отслеживания динамического появления элементов на странице
    const observer = new MutationObserver((mutations, obs) => {
        const logo = document.querySelector('ytd-topbar-logo-renderer');
        if (logo) {
            injectButton();
            // Не отключаем observer полностью, так как при переходах по страницам YouTube интерфейс перерисовывается
        }
    });

    // Запускаем отслеживание изменений в DOM-дереве
    observer.observe(document.body, {
        childList: true,
        subtree: true
    });
})();
