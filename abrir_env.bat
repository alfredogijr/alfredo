@echo off
:: Abre o .env no Bloco de Notas para edicao facil
if not exist .env copy .env.example .env
notepad .env
