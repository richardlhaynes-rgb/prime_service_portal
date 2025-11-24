Category: Design Applications
Subcategory: Autodesk (AutoCAD, Revit, Civil 3D)
Article 1
KB Title: AutoCAD: How to Reset to Default Settings
Problem: AutoCAD is experiencing issues such as:
Toolbars or ribbons are missing
The program is slow, freezes, or crashes
Custom settings have become corrupt
The program is not behaving as expected
Resetting the program to its default settings is the most common and effective solution for a wide range of issues.
Solution: Note: This process will back up and reset your custom settings.
Close all AutoCAD applications.
Open the Windows Start Menu.
Navigate to the folder for your AutoCAD version (e.g., AutoCAD 20xx).
Click the application named "Reset Settings to Default".
A dialog box will open. Choose the "Back up and Reset Custom Settings" option. This will create a backup of your current settings in a ZIP file before resetting.
Allow the reset utility to run. It will re-launch AutoCAD, which will appear as it did on a fresh installation.
Source (for internal reference): https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/How-to-reset-AutoCAD-to-defaults.html

Article 2
KB Title: Civil 3D: How to Clean and Repair a Corrupt Drawing
Problem: A specific drawing file is causing issues:
The file is extremely slow to open or save.
The file size is excessively large.
The program crashes when working in the file.
Errors appear when opening the file.
This is often caused by drawing corruption or an accumulation of unreferenced data ("bloat").
Solution: Perform these steps in order on the problematic drawing file.
AUDIT:
Open the drawing.
In the command line, type AUDIT and press Enter.
Type Y (for Yes) and press Enter to fix any errors detected.
PURGE (Registered Applications):
In the command line, type -PURGE (note the dash at the beginning).
Type R (for RegApps) and press Enter.
Press Enter to accept the default * (asterisk).
Type N (for No) when asked to verify each name, and press Enter.
PURGE (All):
In the command line, type PURGE.
In the dialog box, check all checkboxes (including "Purge nested items").
Click "Purge All". Repeat this process until the "Purge All" button is grayed out.
SAVE:
Save the drawing.
WBLOCK (For severe corruption):
If the steps above are not enough, WBLOCK (Write Block) can export the drawing data to a new, clean file.
Type WBLOCK in the command line.
Select the "Entire drawing" option.
Specify a new file name and location.
Click OK. Open the new file you just created. This file will be "clean" of the corrupt elements.
Source (for internal reference): https://c3dkb.dot.wi.gov/Content/c3d/fil-sftwr-mgt/fil-sftwr-mgt-fix-dmgd-crpt-dwgs.htm

Article 3
KB Title: Revit: How to Improve Slow Performance in a Model
Problem: A Revit model is performing poorly:
It is slow to open, sync, or save.
Navigation (panning, zooming, orbiting) is sluggish.
The program hangs or "thinks" frequently.
Solution: Poor performance is usually caused by model "bloat" or unmanaged warnings.
Audit the Model: When opening the central model, check the "Audit" box. This will scan the model for errors and fix them. This should be done weekly.
Purge Unused:
Go to the "Manage" tab > "Purge Unused".
A dialog box will appear. Click "Check All".
Click OK. This removes all unused families, view templates, and other elements that bloat the file. Run this 2-3 times in a row to remove nested items.
Review Warnings:
Go to the "Manage" tab > "Warnings".
Review the warnings. A high number of warnings (especially "Room/Area is not in a properly enclosed region" or "Highlighted elements overlap") will severely slow down the model.
Fix the most critical warnings.
Disable Add-ins: Temporarily disable all third-party add-ins to see if one of them is causing the slowdown.
Close Inactive Views: Revit only regenerates views that are open. Close all views you are not actively working on to speed up model interactions.
Source (for internal reference): https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/How-to-improve-optimize-or-troubleshoot-model-performance-in-Revit.html

Article 4
KB Title: AutoCAD: Command Line is Missing or Has Disappeared
Problem: The command line, which normally sits at the bottom of the screen, is gone. The user cannot type commands.
Solution:
Press Ctrl+9 (Control key and the number 9) on the keyboard.
This key combination toggles the command line on and off. Pressing it should immediately restore the command line.
If this does not work, type COMMANDLINE and press Enter.
Source (for internal reference): https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Command-line-is-missing-in-AutoCAD.html

Article 5
KB Title: AutoCAD: Plot Style (CTB/STB File) is Missing or Not Found
Problem: When a user goes to plot (print), the "Plot style table" dropdown is blank or missing the company-standard CTB file. The drawing may plot in full color instead of black and white.
Solution:
In the command line, type OPTIONS and press Enter.
Go to the "Files" tab.
Expand "Printer Support File Path".
Expand "Plot Style Table Search Path".
Check the path listed here. It must point to the network folder where the company CTB files are stored.
If the path is missing or incorrect, add the correct path, click Apply, and restart AutoCAD.
Source (for internal reference): https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Error-CTB-or-STB-file-in-AutoCAD-is-not-found-or-missing.html

Article 6
KB Title: AutoCAD: FATAL ERROR - Unhandled Access Violation
Problem: AutoCAD crashes on startup or while opening a file, showing a "FATAL ERROR" message, often mentioning an "unhandled access violation."
Solution: This is often caused by a corrupt user profile or graphics issues.
Disable Hardware Acceleration: Right-click the AutoCAD icon, go to Properties. In the "Target" field, add a space at the end and type /nohardware. Click Apply and try to launch AutoCAD. If it opens, the issue is the graphics driver.
Update the Graphics Driver: Go to the NVIDIA or AMD website and install the latest certified driver for the user's graphics card.
Reset User Profile: If graphics are not the issue, use the "Reset Settings to Default" utility (as described in the KB article "AutoCAD: How to Reset to Default Settings").
Source (for internal reference): https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Fatal-Error-Unhandled-Access-Violation-Reading-0x0000-Exception-at-bcbdad73h.html

Article 7
KB Title: AutoCAD: Cursor is Laggy, Jittery, or Slow
Problem: The mouse cursor in the drawing area is slow, choppy, or lags behind, making it difficult to work.
Solution:
In the command line, type GRAPHICSCONFIG and press Enter.
A dialog box will open. Make sure the "Hardware Acceleration" toggle is set to On.
If it is on, try turning it Off and then back On again.
Also, check that the "2D Display Settings" is set to "Advanced Mode," not "Basic."
If this fails, update the graphics driver.
Source (for internal reference): https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Cursor-is-slow-or-jerky-in-AutoCAD-based-products.html

Article 8
KB Title: Revit: Error "Cannot Synchronize with Central" (Sync Stuck)
Problem: A user tries to "Synchronize with Central" and the process hangs for a long time or fails with a generic error.
Solution:
Check Network: First, ensure the user has a stable connection to the file server.
Check Worksharing Monitor: Have the user open the Worksharing Monitor. See if another user is currently in the middle of a "Sync" or "Save." Tell your user to wait and try again in 5 minutes.
Clear Local File: If the problem continues, the user's local file may be corrupt.
Have the user close Revit.
Go to their local file location, find the local copy of the model, and delete it (along with its backup folder).
Re-open Revit, find the Central Model on the server, and open it. Revit will automatically create a new, clean local copy.
Source (for internal reference): https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Revit-Error-Model-Is-Not-Currently-Available.html

Article 9
KB Title: Revit: Element is Not Visible in a View (Visibility Checklist)
Problem: A user knows they placed an element (like a door, window, or wall) in the model, but it is not appearing in a specific plan view.
Solution: Follow this checklist:
Reveal Hidden Elements: Click the "lightbulb" icon at the bottom of the screen. If the element appears in pink, right-click it and select "Unhide in View."
Visibility/Graphics (VG): Type VG or VV. Check the "Model Categories" tab. Make sure the category (e.g., "Doors") is checked ON.
View Range: In the Properties panel, find "View Range" and click "Edit." Ensure the "Cut Plane" and "View Depth" are set correctly.
Crop Region: Ensure the element is not outside the view's "Crop Region."
Filters: Go to the VG > "Filters" tab. Check if a filter is applied that is hiding the element.
Source (for internal reference): https://hyperfinearchitecture.com/revit-how-to-fix-elements-not-visible/

Article 10
KB Title: Revit: Linked Model (RVT or DWG) is Not Found or Unloaded
Problem: A user opens a Revit model and a linked file (like an architectural background or a DWG site plan) is missing. A "Manage Links" dialog may appear, or the link will show as "Not Found."
Solution: This means Revit has lost the file path to the link.
Go to the "Manage" tab > "Manage Links".
Find the missing link (it will have a "Not Found" status).
Select the link and click "Reload From...".
Navigate to the correct location of the linked file on the server and select it.
Important: If the path type was the problem (e.g., it was "Absolute"), you may need to "Remove" the link and "Add" it back using the "Relative" or "Network Path" setting.
Source (for internal reference): https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Linked-document-not-found-link-will-be-unloaded-appears-when-trying-to-reload-a-linked-BIM-360-model-in-Revit.html

Article 11
KB Title: Revit: How to Repair a Corrupt Family (RFA) File
Problem: A user tries to load a family file (.RFA) into a project and Revit either crashes or gives a "Cannot load family" or "File is corrupt" error.
Solution:
Do NOT load the family directly.
Open your version of Revit without any project open.
Go to File > Open > Family.
Navigate to the corrupt RFA file and select it.
Crucially, check the "Audit" box in the open dialog.
Click "Open." Revit will audit and repair the file.
Once open, go to Manage > Purge Unused. Purge the file to clean it.
Click "Save As" and save the family with a new name (e.g., "Family-Cleaned.rfa").
This new, clean file can now be safely loaded into your project.
Source (for internal reference): https://revitgamers.com/revit-file-corruption/

Article 12
KB Title: Civil 3D: Data Shortcuts are Broken or Missing
Problem: A user opens a drawing and the Civil 3D objects (like surfaces or alignments) that are data-referenced are missing. The "Prospector" tab may show a broken link icon.
Solution:
In the "Toolspace" panel, on the "Prospector" tab, right-click on "Data Shortcuts".
Select "Set Working Folder..."
Navigate to and select the correct project folder that contains the _Shortcuts folder for this project.
Right-click on "Data Shortcuts" again and select "Validate" to refresh.
If links are still broken, right-click the specific item and choose "Repair Broken Reference."
Source (for internal reference): https://resources.imaginit.com/support-blog/civil-3d-surface-disappears-when-data-shortcut-is-refreshed

Article 13
KB Title: Civil 3D: Surface is Not Displaying (No Contours)
Problem: A user has created a surface, or data-referenced a surface, but no contours or triangles are visible in the drawing.
Solution:
Check Surface Style: Right-click on the surface in the Prospector tab > "Surfaces." Go to "Surface Properties..."
On the "Information" tab, check the "Surface Style."
If it is set to "No Display" or "Border Only," change it to a style that shows contours (e.g., "Contours 1' and 5'").
Check Layer: The style might be correct, but the layer it uses may be frozen. Go to the "Display" tab in the Surface Style editor and see which layers the "Major Contour" and "Minor Contour" are on. Then, go to your Layer Manager and make sure those layers are "On" and "Thawed."
Rebuild Surface: Right-click the surface in Prospector and select "Rebuild."
Source (for internal reference): https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Surface-contours-are-not-displayed-in-Autodesk-Civil-3D.html

Article 14
KB Title: Civil 3D: Drawing Contains Proxy Objects (Missing Object Enabler)
Problem: When a user opens a drawing, they get a "Proxy Information" pop-up. The drawing may be missing elements or not display correctly.
Solution:
Identify the Source: Ask the user where the file came from.
Install the Object Enabler: This is the most common fix. The user needs the "AutoCAD Civil 3D Object Enabler" for their version of AutoCAD.
Go to the Autodesk website and search for "Civil 3D [Year] Object Enabler" (e.g., "Civil 3D 2024 Object Enabler").
Download and install this small utility. This allows a plain AutoCAD user (or a user with an older version) to see the custom Civil 3D objects.
If the file came from a newer version (e.g., a 2025 file opened in 2024), the file must be saved down by the sender.
Source (for internal reference): https://help.autodesk.com/view/OARX/2026/ENU/?guid=GUID-1F538CB9-4436-4FF6-8E51-4F5F37191926

Article 15
KB Title: Civil 3D: Survey Database is Locked or Read-Only
Problem: A user tries to edit survey data but finds the survey database is locked or "Read-Only," even when no one else is in it.
Solution: This is often caused by "ghost" lock files that were not removed properly.
Have all users close the survey database.
Using Windows File Explorer, navigate to the folder where the survey database is stored.
Look for hidden files with the same name as the database but with .ldb or .mdw extensions.
Delete these lock files.
Have the user re-open the project. The database should now be accessible.
Source (for internal reference): https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Cannot-edit-survey-code-sets-or-databases.html

Category: Business & Admin Software
Subcategory: Microsoft 365 (Office, Teams, OneDrive)
Article 16
KB Title: Microsoft Office: How to Run an Online Repair
Problem: A Microsoft Office application (Word, Excel, Outlook) is crashing, freezing, or not behaving correctly. Basic troubleshooting (like a reboot) has not fixed the issue.
Solution: An Online Repair will download fresh installation files and fix corrupt Office components.
Close all Microsoft Office applications.
Open the Windows Start Menu and click the Settings gear ⚙.
Click on "Apps" (or "Apps & Features").
Scroll down and find your "Microsoft 365" or "Microsoft Office" installation in the list.
Click on it, then click "Modify".
A new window will appear. Select the "Online Repair" option (do not choose "Quick Repair").
Click "Repair" and follow the prompts. This may take 10-15 minutes and requires an internet connection.
Source (for internal reference): https://support.microsoft.com/en-us/office/repair-an-office-application-7821d4b6-7c1d-4205-aa0e-a6b40c5bb88b

Article 17
KB Title: Microsoft Office: How to Recover an Unsaved Document
Problem: Word, Excel, or PowerPoint crashed, and the user did not save their work.
Solution: Office AutoRecover saves a version in the background every few minutes.
Re-open the application (e.g., Word).
In most cases, a "Document Recovery" pane will automatically open on the left side of the screen, showing available recovered files.
If it does not, go to File > Info > Manage Document (or Manage Workbook/Presentation).
Click "Recover Unsaved Documents".
A folder will open showing unsaved files. Look for the file by date and time, open it, and immediately click "Save As" to save it to a safe location.
Source (for internal reference): https://support.microsoft.com/en-us/office/recover-your-office-files-dc90180f-3f96-480c-b2c3-1c29757f5c81

Article 18
KB Title: Excel: File is "Locked for Editing" by Another User
Problem: A user tries to open an Excel file from a shared drive (like Egnyte or a network server), and they get a message that the file is "locked for editing by [username]," even when that user does not have it open.
Solution: This is caused by a "ghost" lock file that was not deleted.
Have all users close the Excel file.
Using Windows File Explorer, navigate to the folder where the Excel file is located.
Look for a hidden file that has the same name as the Excel file but starts with a tilde and dollar sign (~$) (e.g., ~$ProjectData.xlsx).
Delete this ~$ lock file.
Have the user try to open the main Excel file again. The lock should be gone.
Source (for internal reference): https://support.microsoft.com/en-us/office/excel-file-is-locked-for-editing-6fa938AB-6AB0-4D2A-B3DA-25DAA3F45693

Article 19
KB Title: OneDrive: How to Reset a "Stuck" Sync
Problem: The OneDrive sync client is stuck "Processing Changes," "Syncing," or is not updating with new files from the cloud.
Solution: Resetting OneDrive will force it to re-scan all files without re-downloading them.
Press the Windows Key + R to open the "Run" dialog.
Copy and paste the following command and press Enter: %localappdata%\Microsoft\OneDrive\onedrive.exe /reset
The OneDrive cloud icon in your system tray will disappear and then reappear after a minute or two.
If it does not reappear, open the Start Menu, type "OneDrive," and launch the application manually.
OneDrive will now re-index all files, which may take some time, but it will resolve most sync issues.
Source (for internal reference): https://support.microsoft.com/en-us/office/reset-onedrive-34701e00-bf7b-42db-b960-84905399050c

Subcategory: Email & Outlook
Article 20
KB Title: Outlook: How to Create a New Mail Profile
Problem: Outlook is crashing on startup, will not open, or is having severe performance issues that a repair did not fix. The user's mail profile may be corrupt.
Solution:
Close Outlook.
Open the Windows Start Menu and type "Control Panel".
In the Control Panel, find and click on "Mail (Microsoft Outlook)". (You may need to change "View by" to "Small icons").
In the window that opens, click "Show Profiles...".
Click the "Add..." button to create a new profile.
Give the new profile a name (e.g., "New 2025 Profile").
Follow the prompts to add the user's email account.
After the new profile is created, select the option "Always use this profile" and choose your new profile from the dropdown.
Click OK. Start Outlook. It will open with the fresh settings.
Source (for internal reference): https://support.microsoft.com/en-us/office/create-an-outlook-profile-f544c1ba-3352-4b3b-be0b-8d42a540459d

Article 21
KB Title: Outlook: How to Rebuild the Search Index
Problem: The search function in Outlook is not finding emails, is returning incomplete results, or is very slow.
Solution: This forces Windows to re-index all Outlook items.
In Outlook, click File > Options > Search.
Click the "Indexing Options..." button.
In the new window, click the "Advanced" button.
In the "Troubleshooting" section, click the "Rebuild" button.
Click OK. This process can take a long time (even hours) but can run in the background. Search will be unavailable until it is complete.
Source (for internal reference): https://support.microsoft.com/en-us/office/fix-search-issues-in-outlook-by-rebuilding-your-index-2913adaf-0d49-4a30-b21a-1f8e3f8832ed

Article 22
KB Title: Outlook: How to Clear the Auto-Complete Cache
Problem: When a user types an email address, an old or incorrect suggestion (a "ghost" contact) appears. Or, a user's name has changed and the old one still shows up.
Solution: A. Remove a Single Entry:
Start a new email.
Type the first few letters of the incorrect address.
When the suggestion appears in the list, use the arrow keys to highlight it.
Press the Delete key.
B. Clear the Entire Cache:
In Outlook, go to File > Options > Mail.
Scroll down to the "Send messages" section.
Click the button labeled "Empty Auto-Complete List".
Click Yes to confirm.
Source (for internal reference): https://support.microsoft.com/en-us/office/manage-suggested-recipients-in-the-to-cc-and-bcc-boxes-with-auto-complete-dde4627b-491b-4b21-823a-7d0922851d14

Article 23
KB Title: Outlook: How to Recall a Sent Message
Problem: A user has sent an email by mistake (to the wrong person, or with incorrect information) and wants to recall it.
Solution: Note: This only works if both the sender and the recipient are inside your organization (PRIME) and are on the same Microsoft Exchange server. It will not work for external recipients.
In Outlook, go to your "Sent Items" folder.
Double-click the message you want to recall to open it in a new window.
Go to the "Message" tab, click "Actions" (or "Move" > "More Move Actions").
Click "Recall This Message...".
Select your option (Delete or Delete & Replace) and click OK.
Source (for internal reference): https://support.microsoft.com/en-us/office/recall-or-replace-an-email-message-that-you-sent-35027f88-d655-4554-b4f8-6c0729a723a0

Subcategory: File Storage & Sharing
Article 24
KB Title: Egnyte: How to Restore a Deleted File or Folder
Problem: A user has accidentally deleted a file or folder and needs it restored.
Solution: Egnyte keeps deleted files in the Trash for a set period.
Log in to the Egnyte web portal (e.g., prime.egnyte.com).
In the top right, click the "Apps" menu (grid icon) and select "Trash".
You can search for the file or browse by the folder path it was deleted from.
Find the file or folder you want to restore.
Check the box next to its name.
Click the "Restore" button. The file will be returned to its original folder.
Source (for internal reference): https://help.egnyte.com/hc/en-us/articles/201633304-Trash-and-File-Retention-

Article 25
KB Title: Egnyte: File is Locked by Another User
Problem: A user cannot edit a file stored in Egnyte because it is "locked" by another user. This often happens if the other user's application crashed or they lost their internet connection.
Solution: You can manually unlock the file from the web portal.
Log in to the Egnyte web portal (prime.egnyte.com).
Navigate to the file that is locked.
Click the "..." (More) menu next to the file name.
Select "Unlock". (This option will only appear if the file is locked).
If you do not see the "Unlock" option, you may not have sufficient permissions.
If the file was locked because a user "Checked it out," you may need to ask an Admin to "Discard Check-out" to break the lock.
Source (for internal reference): https://help.egnyte.com/hc/en-us/articles/201633104-File-Locking-and-Versioning

Subcategory: VPN / Remote Access
Article 26
KB Title: FortiClient: Common "Cannot Connect" Troubleshooting
Problem: A user is unable to connect to the company VPN using FortiClient. The connection fails, times out, or gets stuck at a certain percentage.
Solution:
Check Internet: Ensure the user has a stable internet connection. Ask them to visit a website (like google.com) to confirm.
Restart PC: A simple reboot solves many connection-related issues.
Check for Updates: Open the FortiClient Console. Check the "About" or "Settings" page to see if it is running the latest version. If not, run the updater.
Restart the Service:
Press Ctrl+Shift+Esc to open Task Manager.
Go to the "Services" tab.
Find the service named "FortiClient Service Scheduler" (or FA_Scheduler).
Right-click the service and choose "Restart".
Test from a Different Network: If the user is at home, ask them to try connecting from their mobile hotspot. This will determine if their home router or ISP is blocking the connection.
Re-enter Password: If the connection fails at "Credentials," click "Unlock Settings," re-type the password, and try again. The saved password may be incorrect.
Source (for internal reference): https://community.fortinet.com/t5/FortiClient/tkb-p/forticlient

Article 27
KB Title: Windows: How to Clear Cached Credentials for VPN
Problem: A user's VPN (or a mapped network drive) fails to connect, or it won't accept their new password. It keeps trying to log in with their old, "cached" credentials.
Solution: This will clear all saved passwords for network resources from Windows.
Open the Windows Start Menu and type "Credential Manager".
Open the Credential Manager.
Click on "Windows Credentials".
Look through the list under "Generic Credentials" for any saved passwords related to your VPN server address or file server.
Click the arrow to expand the credential, and then click "Remove".
Confirm the removal.
Restart the PC. The next time the user connects, they will be prompted to enter their new credentials.
Source (for internal reference): https://support.microsoft.com/en-us/windows/accessing-credential-manager-1b5c916b-6a16-c3f5-0c7c-ba107E318114

Subcategory: Web Browsers
Article 28
KB Title: Browser: How to Clear Cache and Cookies (Chrome & Edge)
Problem: A website is not loading correctly, showing old information, or giving login errors. This is often caused by a corrupt "cached" version of the site.
Solution: Shortcut (Works for Chrome, Edge, Firefox):
While in the browser, press Ctrl+Shift+Delete.
A "Clear browsing data" window will open.
Set the "Time range" to "All time".
Make sure "Cookies and other site data" and "Cached images and files" are checked.
Click "Clear data" (or "Clear now").
Close and re-open the browser.
Source (for internal reference): https://support.google.com/accounts/answer/32050

Article 29
KB Title: Browser: How to Manage Pop-up Blocker Settings (Chrome & Edge)
Problem: A user is trying to access a legitimate website (like a vendor or banking site) that requires a pop-up window, but the browser is blocking it.
Solution: You can add an "exception" for that specific website.
Go to the website that is being blocked.
Look in the address bar (on the far right). You should see a small icon of a window with a red 'X'.
Click that icon.
A small menu will appear. Select the option "Always allow pop-ups and redirects from [website.com]".
Click "Done".
Refresh the page and try the link again.
Source (for internal reference): https://support.google.com/chrome/answer/95472

Subcategory: Deltek (Vision, Vantagepoint, etc.)
Article 30
KB Title: Deltek (Vantagepoint / EleVia): Login & Connection Issues
Problem:
A user is unable to log in to the Deltek Vantagepoint web portal.
A user receives an error when trying to access or use the Deltek EleVia application.
The user receives an "Invalid username/password" error, even when credentials are correct.
Solution: The correct solution depends on which application you are using.
Part 1: For Deltek Vantagepoint (Web Portal) The Vantagepoint web portal does not require a VPN connection.
Clear Browser Cache: This is the most common fix. A corrupt cache can cause login or display issues. Follow the steps in KB article "Browser: How to Clear Cache and Cookies (Chrome & Edge)".
Check Saved Password: Your browser might be auto-filling an old, incorrect password. Try typing your password manually.
Clear Windows Credentials: If the browser issue continues, Windows may be passing old credentials. Follow the steps in KB article "Windows: How to Clear Cached Credentials for VPN" and remove any saved credentials related to your Deltek website.
Part 2: For Deltek EleVia (Desktop Application) The EleVia application REQUIRES a connection to the FortiClient VPN to function.
Check VPN Connection: You must be connected to the FortiClient VPN. If you are not connected, please connect and try launching EleVia again.
Clear Cached Credentials: If the VPN is connected but EleVia still fails, it may be using an old password. Follow the steps in the KB article "Windows: How to Clear Cached Credentials for VPN" and remove any credentials related to Deltek or EleVia.
Check for "Ghost" Session: If your application crashed, your session might be "stuck." Wait 10-15 minutes and try again. If it still fails, contact an IT admin to clear the locked session from the server.
Source (for internal reference): Internal troubleshooting steps based on PRIME's specific Deltek configuration.

Category: Hardware & Peripherals
Subcategory: Workstations (Desktops, Laptops)
Article 31
KB Title: Laptop: How to Properly Undock/Redock from WAVLINK Dock
Problem: When a user removes their laptop from the WAVLINK dock, or plugs it back in, their monitors, mouse, or keyboard don't work.
Solution: To prevent issues with the DisplayLink drivers, follow this process.
To Undock (Safely):
Save your work and close the laptop lid.
Wait 5-10 seconds for the laptop to enter sleep mode.
Unplug the single USB-C cable that connects to the WAVLINK dock.
To Redock:
Ensure the laptop lid is still closed.
Plug in the USB-C cable from the WAVLINK dock.
Wait 5-10 seconds for the dock and DisplayLink drivers to initialize.
Open the laptop lid or tap your external mouse/keyboard to wake the machine. The monitors should activate.
Source (for internal reference): Best practices for using DisplayLink-based docking stations.

Article 32
KB Title: Laptop: Battery Not Charging or Stuck at 60%/80%
Problem: A user's laptop is plugged in, but the battery is not charging, or it is stuck at 60% or 80%.
Solution:
Check Health Mode (Common Fix): Many high-performance laptops have a utility to protect battery health. This often involves "locking" the charge at 80%.
Open the Start Menu and look for the laptop's built-in support or control center app (e.g., "Creator Center," "MSI Center," or a similar "system control" app).
Find the "Power" or "Battery" settings and look for a "Battery Health" or "Charge Mode" setting.
Set this to "Full Capacity" or "Best for Mobility" to charge to 100%.
Perform a Power-Cycle:
Unplug the laptop from the charger.
Shut down the laptop completely.
Press and hold the power button for 30 seconds.
Re-attach the charger and turn the laptop on.
Update Drivers: Use the manufacturer's built-in update utility to update the system BIOS and Power Management Drivers.
Source (for internal reference): Internal troubleshooting for laptop battery health modes.

Article 33
KB Title: Laptop: How to Fix Slow Performance (Throttling)
Problem: The laptop is hot to the touch, the fan is running constantly at high speed, and applications (especially CAD/Revit) are running very slowly. This is "thermal throttling."
Solution: Overheating is caused by blocked airflow or high resource usage.
Check Airflow: Ensure the laptop's vents (on the bottom and sides) are not blocked by paper, a soft surface (like a bed or lap), or dust.
Elevate the Laptop: Place the laptop on a hard, flat surface. Using a laptop stand will significantly improve airflow.
Check Task Manager: Press Ctrl+Shift+Esc to open Task Manager. Look for any application using a high amount of CPU (e.g., > 30%) that shouldn't be.
Check Power Plan: Go to Control Panel > Power Options. Ensure the "High performance" plan is selected when plugged in. Avoid "Power saver."
Source (for internal reference): Generic steps for diagnosing thermal throttling on high-performance workstations.

Article 34
KB Title: Windows: How to Free Up Hard Drive Space (Disk Cleanup)
Problem: The user is receiving warnings that their C: drive is full, and applications are running slowly.
Solution: Windows has a built-in tool to safely remove old and temporary files.
Open the Start Menu and type "Disk Cleanup".
Select the C: drive and click OK.
The tool will scan for files. In the window that appears, check the boxes for:
Downloaded Program Files
Temporary Internet Files
Recycle Bin
Temporary files
Click the "Clean up system files" button (this is the most important step).
Select the C: drive again. The tool will re-scan.
A new, more advanced list will appear. Check the box for "Windows Update Cleanup" (this can be several GBs).
Click OK and "Delete Files" to begin the cleanup.
Source (for internal reference): https://support.microsoft.com/en-us/windows/disk-cleanup-in-windows-8a96ff42-5751-39ad-9861-346d81be5df3

Article 35
KB Title: Laptop: "No Bootable Device" Error on Startup
Problem: When the user turns on their laptop, it does not load Windows. It shows a black screen with an error like "No Bootable Device Found" or "Boot Device Not Found."
Solution: This means the laptop can't find its hard drive, often because a USB device is confusing it.
Unplug everything. Disconnect the docking station and any other USB drives, mice, or keyboards.
Restart the PC. This is the most common fix, as a connected device was likely interfering with the boot order.
If it still fails, press and hold the power button for 10 seconds to force a shutdown. Wait a moment, then turn it back on.
If the error persists, the hard drive may have failed. This requires an IT technician.
Source (for internal reference): Generic IT troubleshooting steps for boot device errors.

Subcategory: Monitors & Docking Stations
Article 36
KB Title: WAVLINK Dock: Monitors Not Detected (DisplayLink Driver Issue)
Problem: A user plugs their laptop into the WAVLINK dock, but one or both monitors are blank and show "No Signal."
Solution: This is not a standard Thunderbolt dock. It uses DisplayLink technology, which requires a special driver. This driver is the #1 cause of failure.
Power-Cycle the Dock: Unplug the docking station's power cable from the wall. Wait 30 seconds. Plug it back in. This often re-initializes the DisplayLink chip.
Update DisplayLink Driver (The Main Fix):
Go to the Start Menu and search for "DisplayLink Graphics" or "DisplayLink Updater".
If found, run it and check for updates.
If not found, an IT technician must download and install the latest "DisplayLink Driver" from synaptics.com (they bought DisplayLink).
Check Connections: Ensure the USB-C cable is secure in the laptop and the two video cables (HDMI, DisplayPort, etc.) are secure in the dock and the monitors.
Check Monitor Input: Press the "Input" button on the monitor and ensure it is set to the correct video port (e.g., HDMI-1, DisplayPort).
Source (for internal reference): https://support.displaylink.com/knowledgebase/articles/525121-display-not-working-or-goes-blank

Article 37
KB Title: WAVLINK Dock: USB Ports or Ethernet Not Working
Problem: A user's monitors are working, but their wired internet, USB mouse, or keyboard (all plugged into the WAVLINK dock) are not functioning.
Solution: This is often caused by a driver issue, either with the laptop's USB controller or the dock's internal DisplayLink hub.
Re-plug the Dock: Unplug the single USB-C cable from the laptop, wait 10 seconds, and plug it back in.
Power-Cycle the Dock: Unplug the dock's power adapter from the wall, wait 30 seconds, and plug it back in.
Update Laptop Drivers: Use the laptop's built-in support utility or go to the manufacturer's support website. Download and install the latest Chipset and USB drivers.
Re-install DisplayLink Driver: The dock's USB and Ethernet ports are often controlled by the main DisplayLink driver. An IT technician can install the latest version from synaptics.com (they bought DisplayLink) to fix this.
Source (for internal reference): Troubleshooting for DisplayLink hub/port connectivity.

Article 38
KB Title: Windows: How to Change Monitor Arrangement (Display Settings)
Problem: A user's monitors are working, but when they move their mouse, it goes to the wrong screen (e.g., they move the mouse right, and it appears on the far-left monitor).
Solution: Windows' "Display Settings" do not match the physical layout of the desks.
Right-click on the desktop and select "Display settings".
A window will appear with a diagram showing your monitors as numbered boxes (1, 2, 3).
Click the "Identify" button. Numbers will appear on each screen.
In the settings window, click and drag the numbered boxes to match the physical layout on your desk.
Click "Apply" to save the new arrangement.
Source (for internal reference): https://support.microsoft.com/en-us/windows/set-up-dual-monitors-in-windows-3d5c15dc-cc61-d850-aeb0-b419e481b79fff

Article 39
KB Title: Windows: How to Fix Blurry Text on Monitors (ClearType)
Problem: A user's monitor is on and at the correct resolution, but text (especially in emails or websites) looks fuzzy, blurry, or has colored "fringing."
Solution:
Run ClearType:
Open the Start Menu and type "ClearType".
Select the option "Adjust ClearType text".
Make sure the box "Turn on ClearType" is checked and click "Next."
The utility will show you several text samples. Click the text box that looks clearest to you.
Check Monitor Sharpness:
Press the menu/settings button on the monitor itself.
Navigate to the "Image" or "Display" settings.
Find the "Sharpness" setting. If it is very high (e.g., 90-100) or very low, it can cause blur.
Try setting it to a neutral value (e.g., 50).
Source (for internal reference): https://support.microsoft.com/en-us/windows/use-cleartype-in-windows-11-to-make-text-sharper-7d728dae-4a11-4894-814b-253c070932c0

Article 40
KB Title: Monitor: No Signal or "Input Not Supported" Error
Problem: A monitor is black and says "No Signal," or it flashes a message like "Input Not Supported" or "Out of Range."
Solution:
"No Signal": This means the monitor is not receiving a connection from the computer.
Check that the video cable (e.g., HDMI, DisplayPort) is firmly seated in the docking station or laptop port and in the monitor.
Press the "Input" or "Source" button on the monitor and cycle through the inputs (e.g., HDMI-1, HDMI-2, DisplayPort) until the picture appears.
"Input Not Supported": This means the laptop is sending a resolution or refresh rate the monitor can't handle.
Follow the steps in the KB article "Windows: How to Change Monitor Arrangement (Display Settings)".
Select the problematic monitor.
Set the "Display resolution" to a standard, supported setting (e.g., 1920 x 1080).
Set the "Refresh rate" to a standard value (e.g., 60Hz).
Source (for internal reference): Generic IT troubleshooting steps for monitor signal issues.

Subcategory: Mobile Devices (iPhones, iPads)
Article 41
KB Title: Mobile Device: How to Set Up Company Email (Outlook App)
Problem: A user needs to get their PRIME email, calendar, and contacts on their iPhone or Android device.
Solution: For security, do not use the native "Mail" app. You must use the official Microsoft Outlook app.
Go to the App Store (iPhone) or Google Play Store (Android).
Search for and download "Microsoft Outlook".
Open the Outlook app.
When prompted to add an account, enter your full PRIME email address (e.g., user@primeeng.com).
Click "Add Account".
You will be redirected to the PRIME login page.
Enter your password when prompted.
You will then be prompted for 2FA/MFA. Approve the login using the Duo Mobile application on your device.
Your email and calendar will begin syncing to the app.
IT Rationale (for internal reference): We specifically require the Microsoft Outlook app instead of native mail apps (like Apple Mail) for three main reasons:
Security & Control (Main Reason):
Selective Wipe: If a phone is lost or an employee leaves, IT can wipe only the Outlook app and its data, leaving all personal photos and files untouched. Wiping a native mail app often requires wiping the entire device.
App-Level PIN: We can enforce a separate PIN/Face ID just to open the Outlook app, adding a layer of security even if the phone is unlocked.
Data Protection: We can prevent users from copying sensitive company data out of Outlook and into personal apps (like a personal notepad or email).
Features & Compatibility:
The Outlook app fully supports all Microsoft 365 features, such as shared calendars, scheduling tools, and sensitivity labels, which often break or don't work in native apps.
Compliance:
Using a managed app helps us prove that company data is secured according to our policies, which is critical for client data and compliance.
Source (for internal reference): https://support.microsoft.com/en-us/office/set-up-email-in-the-outlook-for-android-app-886db551-8dfa-4fd5-b835-f8e53609eFF1

Article 42
KB Title: Mobile Device: How to Fix Outlook App Sync Issues
Problem: A user's Outlook app on their iPhone or Android is not receiving new emails, or their calendar is not updating. The app may show "Up to date" but new mail is missing.
Solution: This is a common sync issue, usually fixed within the app.
Method 1: Reset the Account (Easiest Fix)
Open the Outlook App.
Tap the Home icon (or your profile picture) in the top-left corner.
Tap the Settings gear ⚙ in the bottom-left corner.
Select your user@primeeng.com email account.
Scroll to the bottom and tap "Reset Account".
The app will restart and re-sync all data from the server. This fixes most issues.
Method 2: Force Quit and Re-open
Force-quit the Outlook app (on iPhone, swipe up from the bottom; on Android, use the app-switcher).
Re-open the app. This can sometimes force a new connection.
Method 3: Clear the Cache (Android Only)
Go to Settings > Apps > Outlook.
Tap "Storage".
Tap "Clear Cache".
Source (for internal reference): https://support.microsoft.com/en-us/office/how-can-i-troubleshoot-sync-issues-with-the-outlook-for-android-app-672e3795-c1e1-450f-a492-c4e9d5696174

Subcategory: Conference Room AV
Article 43
KB Title: Conference Room: How to Connect a Laptop to the TV/Display
Problem: A user needs to present their laptop screen on the main conference room TV.
Solution: Method 1: Wired Connection (Most Reliable)
Locate the HDMI cable on the conference table.
Plug the HDMI cable firmly into your laptop's HDMI port (most laptops have one).
Use the TV remote or wall control panel.
Find the "Input" or "Source" button.
Select the correct input (e.g., HDMI 1, HDMI 2).
Your screen should appear. If not, press Windows Key + P on your laptop and select "Duplicate".
Method 2: Wireless (If available)
Follow the specific instructions for the wireless device in that room (e.g., "Use the Teams Cast button" or "Plug in the ClickShare dongle").
Source (for internal reference): General AV troubleshooting steps for conference rooms.

Article 44
KB Title: Conference Room: No Audio in Teams/Zoom Call (Check Devices)
Problem: A user is in a Teams or Zoom call in a conference room. They can see the video, but they either can't hear anyone, or no one can hear them.
Solution: The wrong audio device is selected in the software.
In the Teams/Zoom call window, find the Settings menu (usually a "..." or gear icon).
Go to "Device settings" or "Audio settings".
Look for the "Speaker" and "Microphone" dropdowns.
The selected device is likely "Laptop Speaker."
Change both the "Speaker" and "Microphone" to the conference room's AV system (e.g., "Room System," "Logitech," or "Echo Cancelling Speakerphone").
You should immediately hear audio, and others should be able to hear you.
Source (for internal reference): https://support.microsoft.com/en-us/office/manage-your-call-settings-in-microsoft-teams-911D551B-EAF3-4B07-88F8-88F23631A91B

Subcategory: Specialty Peripherals (3Dconnexion mouse, etc.)
Article 45
KB Title: 3D Mouse: 3Dconnexion SpaceMouse Not Working in 3ds Max
Problem: A user's 3Dconnexion SpaceMouse (3D puck) works on the desktop but does not function (or stops working) inside 3ds Max.
Solution: This means the specific add-in for 3ds Max is missing, disabled, or corrupt. This often happens after a 3ds Max update.
Check 3ds Max Driver: In 3ds Max, go to the Customize > Preferences... menu. Find the "3Dconnexion" tab and ensure the device is enabled. If the tab is missing, the driver is not loading.
Re-run the Driver (The Main Fix): The easiest and most reliable fix is to re-install the 3Dconnexion add-ins.
Go to the 3Dconnexion website and download the latest 3DxWare driver.
Close 3ds Max. This is a critical step.
Run the 3DxWare installer you just downloaded. It will detect your installed version of 3ds Max and re-install the plug-in for it.
Restart your PC and open 3ds Max. The 3D mouse should now be functional.
Source (for internal reference): https://3dconnexion.com/us/support/faq/my-3dconnexion-mouse-is-not-working-in-my-application-after-i-updated-it/