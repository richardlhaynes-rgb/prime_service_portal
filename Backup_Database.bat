@echo off
set PGPASSWORD=admin
echo Backing up PRIME Service Portal Database...
"C:\Program Files\PostgreSQL\15\bin\pg_dump.exe" -U postgres prime_service_portal > portal_db_backup.sql
echo Backup Complete: portal_db_backup.sql
pause