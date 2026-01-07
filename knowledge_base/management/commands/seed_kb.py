from django.core.management.base import BaseCommand
from django.db import connection
from knowledge_base.models import Article

class Command(BaseCommand):
    help = 'Seeds the Knowledge Base with 45 detailed IT articles. Use --clear to wipe only.'

    def add_arguments(self, parser):
        parser.add_argument('--clear', action='store_true', help='Wipe KB without reseeding.')

    def handle(self, *args, **kwargs):
        self.stdout.write("--- Seeding Knowledge Base (Full 45 Articles) ---")

        # 1. HARD WIPE (Resets IDs to 1)
        with connection.cursor() as cursor:
            # Adjust table name if needed based on app label
            cursor.execute("TRUNCATE TABLE knowledge_base_article RESTART IDENTITY CASCADE;")
            self.stdout.write(self.style.SUCCESS("Table truncated. IDs reset to 1."))

        if kwargs['clear']:
            self.stdout.write(self.style.SUCCESS(" > OPERATION COMPLETE: KB is empty."))
            return

        # Full dataset parsed from kb_source.md
        articles = [
            # --- Category: Design Applications ---
            {
                "title": "AutoCAD: How to Reset to Default Settings",
                "category": Article.Category.DESIGN_APPS,
                "subcategory": "Autodesk (AutoCAD, Revit, Civil 3D)",
                "problem": "AutoCAD is experiencing issues such as:\n- Toolbars or ribbons are missing\n- The program is slow, freezes, or crashes\n- Custom settings have become corrupt\n- The program is not behaving as expected",
                "solution": "Note: This process will back up and reset your custom settings.\n1. Close all AutoCAD applications.\n2. Open the Windows Start Menu.\n3. Navigate to the folder for your AutoCAD version (e.g., AutoCAD 20xx).\n4. Click the application named 'Reset Settings to Default'.\n5. A dialog box will open. Choose the 'Back up and Reset Custom Settings' option. This will create a backup of your current settings in a ZIP file before resetting.\n6. Allow the reset utility to run. It will re-launch AutoCAD, which will appear as it did on a fresh installation.",
                "internal_notes": "Source: https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/How-to-reset-AutoCAD-to-defaults.html",
                "status": Article.Status.APPROVED
            },
            {
                "title": "Civil 3D: How to Clean and Repair a Corrupt Drawing",
                "category": Article.Category.DESIGN_APPS,
                "subcategory": "Autodesk (AutoCAD, Revit, Civil 3D)",
                "problem": "A specific drawing file is causing issues:\n- The file is extremely slow to open or save.\n- The file size is excessively large.\n- The program crashes when working in the file.\n- Errors appear when opening the file.\n\nThis is often caused by drawing corruption or an accumulation of unreferenced data ('bloat').",
                "solution": "Perform these steps in order on the problematic drawing file.\n\nAUDIT:\n1. Open the drawing.\n2. In the command line, type AUDIT and press Enter.\n3. Type Y (for Yes) and press Enter to fix any errors detected.\n\nPURGE (Registered Applications):\n1. In the command line, type -PURGE (note the dash at the beginning).\n2. Type R (for RegApps) and press Enter.\n3. Press Enter to accept the default * (asterisk).\n4. Type N (for No) when asked to verify each name, and press Enter.\n\nPURGE (All):\n1. In the command line, type PURGE.\n2. In the dialog box, check all checkboxes (including 'Purge nested items').\n3. Click 'Purge All'. Repeat this process until the 'Purge All' button is grayed out.\n\nSAVE:\n1. Save the drawing.\n\nWBLOCK (For severe corruption):\nIf the steps above are not enough, WBLOCK (Write Block) can export the drawing data to a new, clean file.\n1. Type WBLOCK in the command line.\n2. Select the 'Entire drawing' option.\n3. Specify a new file name and location.\n4. Click OK. Open the new file you just created.",
                "internal_notes": "Source: https://c3dkb.dot.wi.gov/Content/c3d/fil-sftwr-mgt/fil-sftwr-mgt-fix-dmgd-crpt-dwgs.htm",
                "status": Article.Status.APPROVED
            },
            {
                "title": "Revit: How to Improve Slow Performance in a Model",
                "category": Article.Category.DESIGN_APPS,
                "subcategory": "Autodesk (AutoCAD, Revit, Civil 3D)",
                "problem": "A Revit model is performing poorly:\n- It is slow to open, sync, or save.\n- Navigation (panning, zooming, orbiting) is sluggish.\n- The program hangs or 'thinks' frequently.",
                "solution": "Poor performance is usually caused by model 'bloat' or unmanaged warnings.\n\n1. Audit the Model: When opening the central model, check the 'Audit' box. This will scan the model for errors and fix them. This should be done weekly.\n2. Purge Unused: Go to the 'Manage' tab > 'Purge Unused'. Click 'Check All', then OK. Run this 2-3 times.\n3. Review Warnings: Go to the 'Manage' tab > 'Warnings'. Fix critical warnings (especially overlapping elements).\n4. Disable Add-ins: Temporarily disable third-party add-ins to test for conflicts.\n5. Close Inactive Views: Close views you are not actively using.",
                "internal_notes": "Source: https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/How-to-improve-optimize-or-troubleshoot-model-performance-in-Revit.html",
                "status": Article.Status.APPROVED
            },
            {
                "title": "AutoCAD: Command Line is Missing or Has Disappeared",
                "category": Article.Category.DESIGN_APPS,
                "subcategory": "Autodesk (AutoCAD, Revit, Civil 3D)",
                "problem": "The command line, which normally sits at the bottom of the screen, is gone. The user cannot type commands.",
                "solution": "1. Press Ctrl+9 (Control key and the number 9) on the keyboard. This toggles the command line.\n2. If this does not work, type COMMANDLINE and press Enter (even if you can't see the text, it will register).",
                "internal_notes": "Source: https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Command-line-is-missing-in-AutoCAD.html",
                "status": Article.Status.APPROVED
            },
            {
                "title": "AutoCAD: Plot Style (CTB/STB File) is Missing or Not Found",
                "category": Article.Category.DESIGN_APPS,
                "subcategory": "Autodesk (AutoCAD, Revit, Civil 3D)",
                "problem": "When a user goes to plot (print), the 'Plot style table' dropdown is blank or missing the company-standard CTB file. The drawing may plot in full color instead of black and white.",
                "solution": "1. In the command line, type OPTIONS and press Enter.\n2. Go to the 'Files' tab.\n3. Expand 'Printer Support File Path'.\n4. Expand 'Plot Style Table Search Path'.\n5. Check the path listed here. It must point to the network folder where the company CTB files are stored.\n6. If the path is missing or incorrect, add the correct path, click Apply, and restart AutoCAD.",
                "internal_notes": "Source: https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Error-CTB-or-STB-file-in-AutoCAD-is-not-found-or-missing.html",
                "status": Article.Status.APPROVED
            },
            {
                "title": "AutoCAD: FATAL ERROR - Unhandled Access Violation",
                "category": Article.Category.DESIGN_APPS,
                "subcategory": "Autodesk (AutoCAD, Revit, Civil 3D)",
                "problem": "AutoCAD crashes on startup or while opening a file, showing a 'FATAL ERROR' message, often mentioning an 'unhandled access violation.'",
                "solution": "This is often caused by a corrupt user profile or graphics issues.\n\n1. Disable Hardware Acceleration: Right-click the AutoCAD icon, go to Properties. In the 'Target' field, add a space at the end and type /nohardware. Click Apply and try to launch.\n2. Update the Graphics Driver: Install the latest certified driver from NVIDIA/AMD.\n3. Reset User Profile: Use the 'Reset Settings to Default' utility.",
                "internal_notes": "Source: https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Fatal-Error-Unhandled-Access-Violation-Reading-0x0000-Exception-at-bcbdad73h.html",
                "status": Article.Status.APPROVED
            },
            {
                "title": "AutoCAD: Cursor is Laggy, Jittery, or Slow",
                "category": Article.Category.DESIGN_APPS,
                "subcategory": "Autodesk (AutoCAD, Revit, Civil 3D)",
                "problem": "The mouse cursor in the drawing area is slow, choppy, or lags behind, making it difficult to work.",
                "solution": "1. In the command line, type GRAPHICSCONFIG and press Enter.\n2. Make sure the 'Hardware Acceleration' toggle is set to On.\n3. If it is on, try turning it Off and then back On again.\n4. Check that '2D Display Settings' is set to 'Advanced Mode' (not Basic).",
                "internal_notes": "Source: https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Cursor-is-slow-or-jerky-in-AutoCAD-based-products.html",
                "status": Article.Status.APPROVED
            },
            {
                "title": "Revit: Error 'Cannot Synchronize with Central' (Sync Stuck)",
                "category": Article.Category.DESIGN_APPS,
                "subcategory": "Autodesk (AutoCAD, Revit, Civil 3D)",
                "problem": "A user tries to 'Synchronize with Central' and the process hangs for a long time or fails with a generic error.",
                "solution": "1. Check Network: Ensure a stable connection to the file server.\n2. Check Worksharing Monitor: See if another user is currently syncing. Wait 5 minutes if so.\n3. Clear Local File: If the problem continues, delete the local copy of the model and its backup folder. Re-open the Central Model to create a fresh local copy.",
                "internal_notes": "Source: https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Revit-Error-Model-Is-Not-Currently-Available.html",
                "status": Article.Status.APPROVED
            },
            {
                "title": "Revit: Element is Not Visible in a View (Visibility Checklist)",
                "category": Article.Category.DESIGN_APPS,
                "subcategory": "Autodesk (AutoCAD, Revit, Civil 3D)",
                "problem": "A user knows they placed an element (like a door or wall) in the model, but it is not appearing in a specific plan view.",
                "solution": "Follow this checklist:\n1. Reveal Hidden Elements: Click the lightbulb icon. If pink, right-click and 'Unhide in View'.\n2. Visibility/Graphics (VG): Check if the category is turned on in the Model Categories tab.\n3. View Range: Ensure the Cut Plane and View Depth are correct.\n4. Crop Region: Ensure the element is inside the crop region.\n5. Filters: Check VG > Filters for any filters hiding the element.",
                "internal_notes": "Source: https://hyperfinearchitecture.com/revit-how-to-fix-elements-not-visible/",
                "status": Article.Status.APPROVED
            },
            {
                "title": "Revit: Linked Model (RVT or DWG) is Not Found or Unloaded",
                "category": Article.Category.DESIGN_APPS,
                "subcategory": "Autodesk (AutoCAD, Revit, Civil 3D)",
                "problem": "A user opens a Revit model and a linked file (like an architectural background) is missing. A 'Manage Links' dialog may appear.",
                "solution": "1. Go to the 'Manage' tab > 'Manage Links'.\n2. Find the missing link (Status: 'Not Found').\n3. Select it and click 'Reload From...'.\n4. Navigate to the correct file location.\n5. If pathing issues persist, remove and re-add the link using 'Relative' or 'Network Path'.",
                "internal_notes": "Source: https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Linked-document-not-found-link-will-be-unloaded-appears-when-trying-to-reload-a-linked-BIM-360-model-in-Revit.html",
                "status": Article.Status.APPROVED
            },
            {
                "title": "Revit: How to Repair a Corrupt Family (RFA) File",
                "category": Article.Category.DESIGN_APPS,
                "subcategory": "Autodesk (AutoCAD, Revit, Civil 3D)",
                "problem": "A user tries to load a family file (.RFA) into a project and Revit crashes or gives a 'File is corrupt' error.",
                "solution": "1. Do NOT load the family directly.\n2. Open Revit (no project).\n3. Go to File > Open > Family.\n4. Select the file and CHECK the 'Audit' box.\n5. Click Open. Revit will repair it.\n6. Purge Unused, then Save As a new name.\n7. Load the new file into the project.",
                "internal_notes": "Source: https://revitgamers.com/revit-file-corruption/",
                "status": Article.Status.APPROVED
            },
            {
                "title": "Civil 3D: Data Shortcuts are Broken or Missing",
                "category": Article.Category.DESIGN_APPS,
                "subcategory": "Autodesk (AutoCAD, Revit, Civil 3D)",
                "problem": "Civil 3D objects (surfaces, alignments) are missing from the drawing. The Prospector tab shows broken link icons.",
                "solution": "1. In 'Toolspace' > 'Prospector', right-click 'Data Shortcuts'.\n2. Select 'Set Working Folder...' and choose the correct project folder.\n3. Right-click 'Data Shortcuts' again and select 'Validate'.\n4. If links remain broken, right-click the item and choose 'Repair Broken Reference'.",
                "internal_notes": "Source: https://resources.imaginit.com/support-blog/civil-3d-surface-disappears-when-data-shortcut-is-refreshed",
                "status": Article.Status.APPROVED
            },
            {
                "title": "Civil 3D: Surface is Not Displaying (No Contours)",
                "category": Article.Category.DESIGN_APPS,
                "subcategory": "Autodesk (AutoCAD, Revit, Civil 3D)",
                "problem": "A surface exists but no contours are visible.",
                "solution": "1. Check Surface Style: Right-click surface > Surface Properties. Change style to 'Contours 1 and 5'.\n2. Check Layers: Go to the Surface Style 'Display' tab. Note the layers for Major/Minor contours. Ensure those layers are On and Thawed in the Layer Manager.\n3. Rebuild: Right-click surface > Rebuild.",
                "internal_notes": "Source: https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Surface-contours-are-not-displayed-in-Autodesk-Civil-3D.html",
                "status": Article.Status.APPROVED
            },
            {
                "title": "Civil 3D: Drawing Contains Proxy Objects (Missing Object Enabler)",
                "category": Article.Category.DESIGN_APPS,
                "subcategory": "Autodesk (AutoCAD, Revit, Civil 3D)",
                "problem": "User gets a 'Proxy Information' popup when opening a file. Elements are missing.",
                "solution": "1. The user needs the 'AutoCAD Civil 3D Object Enabler'.\n2. Go to Autodesk website, search for 'Civil 3D [Year] Object Enabler'.\n3. Download and install to allow plain AutoCAD to view Civil 3D objects.",
                "internal_notes": "Source: https://help.autodesk.com/view/OARX/2026/ENU/?guid=GUID-1F538CB9-4436-4FF6-8E51-4F5F37191926",
                "status": Article.Status.APPROVED
            },
            {
                "title": "Civil 3D: Survey Database is Locked or Read-Only",
                "category": Article.Category.DESIGN_APPS,
                "subcategory": "Autodesk (AutoCAD, Revit, Civil 3D)",
                "problem": "Survey database is locked even when no one is in it.",
                "solution": "1. Have all users close the survey database.\n2. In File Explorer, go to the survey database folder.\n3. Delete any hidden files ending in .ldb or .mdw (lock files).\n4. Re-open the project.",
                "internal_notes": "Source: https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Cannot-edit-survey-code-sets-or-databases.html",
                "status": Article.Status.APPROVED
            },

            # --- Category: Business & Admin Software ---
            {
                "title": "Microsoft Office: How to Run an Online Repair",
                "category": Article.Category.BUSINESS_ADMIN,
                "subcategory": "Microsoft 365 (Office, Teams, OneDrive)",
                "problem": "Office apps (Word, Excel) are crashing or freezing.",
                "solution": "1. Close all Office apps.\n2. Go to Settings > Apps.\n3. Find Microsoft 365/Office, click Modify.\n4. Select 'Online Repair' (Not Quick Repair) and click Repair.\n5. Wait 10-15 minutes.",
                "internal_notes": "Source: https://support.microsoft.com/en-us/office/repair-an-office-application-7821d4b6-7c1d-4205-aa0e-a6b40c5bb88b",
                "status": Article.Status.APPROVED
            },
            {
                "title": "Microsoft Office: How to Recover an Unsaved Document",
                "category": Article.Category.BUSINESS_ADMIN,
                "subcategory": "Microsoft 365 (Office, Teams, OneDrive)",
                "problem": "User closed Word/Excel without saving.",
                "solution": "1. Re-open the app.\n2. Check 'Document Recovery' pane on the left.\n3. If not there, go to File > Info > Manage Document > Recover Unsaved Documents.\n4. Open the file and Save As immediately.",
                "internal_notes": "Source: https://support.microsoft.com/en-us/office/recover-your-office-files-dc90180f-3f96-480c-b2c3-1c29757f5c81",
                "status": Article.Status.APPROVED
            },
            {
                "title": "Excel: File is 'Locked for Editing' by Another User",
                "category": Article.Category.BUSINESS_ADMIN,
                "subcategory": "Microsoft 365 (Office, Teams, OneDrive)",
                "problem": "Excel says file is locked by a user who doesn't have it open.",
                "solution": "1. Ensure no one has the file open.\n2. Navigate to the folder in File Explorer.\n3. Delete the hidden lock file (starts with ~$).\n4. Try opening again.",
                "internal_notes": "Source: https://support.microsoft.com/en-us/office/excel-file-is-locked-for-editing-6fa938AB-6AB0-4D2A-B3DA-25DAA3F45693",
                "status": Article.Status.APPROVED
            },
            {
                "title": "OneDrive: How to Reset a 'Stuck' Sync",
                "category": Article.Category.BUSINESS_ADMIN,
                "subcategory": "Microsoft 365 (Office, Teams, OneDrive)",
                "problem": "OneDrive sync is stuck processing changes.",
                "solution": "1. Press Windows + R.\n2. Run: %localappdata%\\Microsoft\\OneDrive\\onedrive.exe /reset\n3. Wait for the cloud icon to disappear and reappear.\n4. If it doesn't reappear, launch OneDrive manually from Start.",
                "internal_notes": "Source: https://support.microsoft.com/en-us/office/reset-onedrive-34701e00-bf7b-42db-b960-84905399050c",
                "status": Article.Status.APPROVED
            },
            {
                "title": "Outlook: How to Create a New Mail Profile",
                "category": Article.Category.BUSINESS_ADMIN,
                "subcategory": "Email & Outlook",
                "problem": "Outlook crashing or corrupt.",
                "solution": "1. Close Outlook.\n2. Open Control Panel > Mail.\n3. Click 'Show Profiles' > 'Add'.\n4. Name the new profile and follow prompts.\n5. Select 'Always use this profile' and choose the new one.",
                "internal_notes": "Source: https://support.microsoft.com/en-us/office/create-an-outlook-profile-f544c1ba-3352-4b3b-be0b-8d42a540459d",
                "status": Article.Status.APPROVED
            },
            {
                "title": "Outlook: How to Rebuild the Search Index",
                "category": Article.Category.BUSINESS_ADMIN,
                "subcategory": "Email & Outlook",
                "problem": "Outlook search returns incomplete or no results.",
                "solution": "1. File > Options > Search > Indexing Options.\n2. Click Advanced > Rebuild.\n3. Allow time for background re-indexing.",
                "internal_notes": "Source: https://support.microsoft.com/en-us/office/fix-search-issues-in-outlook-by-rebuilding-your-index-2913adaf-0d49-4a30-b21a-1f8e3f8832ed",
                "status": Article.Status.APPROVED
            },
            {
                "title": "Outlook: How to Clear the Auto-Complete Cache",
                "category": Article.Category.BUSINESS_ADMIN,
                "subcategory": "Email & Outlook",
                "problem": "Old email addresses appear in suggestions.",
                "solution": "Single Entry: Type address, press Delete key when suggestion appears.\nFull Clear: File > Options > Mail > Send messages > Empty Auto-Complete List.",
                "internal_notes": "Source: https://support.microsoft.com/en-us/office/manage-suggested-recipients-in-the-to-cc-and-bcc-boxes-with-auto-complete-dde4627b-491b-4b21-823a-7d0922851d14",
                "status": Article.Status.APPROVED
            },
            {
                "title": "Outlook: How to Recall a Sent Message",
                "category": Article.Category.BUSINESS_ADMIN,
                "subcategory": "Email & Outlook",
                "problem": "User sent email by mistake.",
                "solution": "Note: Only works for internal recipients on Exchange.\n1. Open message in Sent Items.\n2. Actions > Recall This Message.\n3. Select Delete or Replace.",
                "internal_notes": "Source: https://support.microsoft.com/en-us/office/recall-or-replace-an-email-message-that-you-sent-35027f88-d655-4554-b4f8-6c0729a723a0",
                "status": Article.Status.APPROVED
            },
            {
                "title": "Egnyte: How to Restore a Deleted File or Folder",
                "category": Article.Category.BUSINESS_ADMIN,
                "subcategory": "File Storage & Sharing",
                "problem": "User deleted a file.",
                "solution": "1. Log in to Egnyte web portal.\n2. Apps menu > Trash.\n3. Find file, check box, click Restore.",
                "internal_notes": "Source: https://help.egnyte.com/hc/en-us/articles/201633304-Trash-and-File-Retention-",
                "status": Article.Status.APPROVED
            },
            {
                "title": "Egnyte: File is Locked by Another User",
                "category": Article.Category.BUSINESS_ADMIN,
                "subcategory": "File Storage & Sharing",
                "problem": "File locked by user who isn't editing it.",
                "solution": "1. Log in to Egnyte web portal.\n2. Navigate to file.\n3. Click '...' > Unlock.\n4. If checked out, ask Admin to 'Discard Check-out'.",
                "internal_notes": "Source: https://help.egnyte.com/hc/en-us/articles/201633104-File-Locking-and-Versioning",
                "status": Article.Status.APPROVED
            },
            {
                "title": "FortiClient: Common 'Cannot Connect' Troubleshooting",
                "category": Article.Category.NETWORKING,
                "subcategory": "VPN / Remote Access",
                "problem": "VPN fails to connect (stuck at 98% or error).",
                "solution": "1. Check internet.\n2. Restart PC.\n3. Restart 'FortiClient Service Scheduler' in Task Manager > Services.\n4. Test from mobile hotspot to rule out home ISP issues.",
                "internal_notes": "Source: https://community.fortinet.com/t5/FortiClient/tkb-p/forticlient",
                "status": Article.Status.APPROVED
            },
            {
                "title": "Windows: How to Clear Cached Credentials for VPN",
                "category": Article.Category.NETWORKING,
                "subcategory": "VPN / Remote Access",
                "problem": "VPN won't accept new password.",
                "solution": "1. Start > Credential Manager.\n2. Windows Credentials.\n3. Remove any entries for VPN or file server.\n4. Restart PC.",
                "internal_notes": "Source: https://support.microsoft.com/en-us/windows/accessing-credential-manager-1b5c916b-6a16-c3f5-0c7c-ba107E318114",
                "status": Article.Status.APPROVED
            },
            {
                "title": "Browser: How to Clear Cache and Cookies (Chrome & Edge)",
                "category": Article.Category.BUSINESS_ADMIN,
                "subcategory": "Web Browsers",
                "problem": "Website loading errors or old data.",
                "solution": "1. Ctrl+Shift+Delete.\n2. Time range: All time.\n3. Check Cookies and Cached images.\n4. Click Clear data.",
                "internal_notes": "Source: https://support.google.com/accounts/answer/32050",
                "status": Article.Status.APPROVED
            },
            {
                "title": "Browser: How to Manage Pop-up Blocker Settings",
                "category": Article.Category.BUSINESS_ADMIN,
                "subcategory": "Web Browsers",
                "problem": "Site blocking necessary pop-ups.",
                "solution": "1. Go to site.\n2. Click icon with red 'X' in address bar.\n3. Select 'Always allow pop-ups from...'.\n4. Done.",
                "internal_notes": "Source: https://support.google.com/chrome/answer/95472",
                "status": Article.Status.APPROVED
            },
            {
                "title": "Deltek (Vantagepoint / EleVia): Login & Connection Issues",
                "category": Article.Category.BUSINESS_ADMIN,
                "subcategory": "Deltek (Vision, Vantagepoint, etc.)",
                "problem": "Login failure or connection error.",
                "solution": "Vantagepoint (Web): Clear browser cache. Remove saved passwords.\nEleVia (App): Requires VPN. Connect FortiClient. Clear Windows Credentials if password fails.",
                "internal_notes": "Internal steps.",
                "status": Article.Status.APPROVED
            },

            # --- Category: Hardware & Peripherals ---
            {
                "title": "Laptop: How to Properly Undock/Redock from WAVLINK Dock",
                "category": Article.Category.HARDWARE,
                "subcategory": "Workstations (Desktops, Laptops)",
                "problem": "Monitors don't wake up after redocking.",
                "solution": "Undock: Close lid, wait for sleep, unplug USB-C.\nRedock: Leave lid closed, plug in USB-C, wait 10s for drivers, then open lid.",
                "internal_notes": "DisplayLink best practices.",
                "status": Article.Status.APPROVED
            },
            {
                "title": "Laptop: Battery Not Charging or Stuck at 60%/80%",
                "category": Article.Category.HARDWARE,
                "subcategory": "Workstations (Desktops, Laptops)",
                "problem": "Battery won't charge to 100%.",
                "solution": "1. Check manufacturer app (Dell/MSI Center) for 'Battery Health' or 'Conservation Mode'. Switch to 'Full Capacity'.\n2. Power cycle: Shut down, hold power 30s.",
                "internal_notes": "Internal note.",
                "status": Article.Status.APPROVED
            },
            {
                "title": "Laptop: How to Fix Slow Performance (Throttling)",
                "category": Article.Category.HARDWARE,
                "subcategory": "Workstations (Desktops, Laptops)",
                "problem": "Laptop hot, fans loud, slow performance.",
                "solution": "1. Check airflow (vents blocked?).\n2. Elevate laptop.\n3. Check Task Manager for high CPU.\n4. Power Options: High Performance.",
                "internal_notes": "Thermal throttling diagnosis.",
                "status": Article.Status.APPROVED
            },
            {
                "title": "Windows: How to Free Up Hard Drive Space (Disk Cleanup)",
                "category": Article.Category.HARDWARE,
                "subcategory": "Workstations (Desktops, Laptops)",
                "problem": "C: Drive full.",
                "solution": "1. Start > Disk Cleanup.\n2. Select C:.\n3. Click 'Clean up system files'.\n4. Check 'Windows Update Cleanup' (reclaims GBs).",
                "internal_notes": "Source: https://support.microsoft.com/en-us/windows/disk-cleanup-in-windows-8a96ff42-5751-39ad-9861-346d81be5df3",
                "status": Article.Status.APPROVED
            },
            {
                "title": "Laptop: 'No Bootable Device' Error on Startup",
                "category": Article.Category.HARDWARE,
                "subcategory": "Workstations (Desktops, Laptops)",
                "problem": "Black screen with boot error.",
                "solution": "1. Unplug ALL USB devices/docks (interferes with boot order).\n2. Restart.\n3. If fails, hard reset (hold power 10s).",
                "internal_notes": "Standard boot troubleshooting.",
                "status": Article.Status.APPROVED
            },
            {
                "title": "WAVLINK Dock: Monitors Not Detected (DisplayLink Driver Issue)",
                "category": Article.Category.HARDWARE,
                "subcategory": "Monitors & Docking Stations",
                "problem": "Monitors blank/No Signal on dock.",
                "solution": "1. Power cycle dock (unplug power, wait 30s).\n2. Update 'DisplayLink Graphics' driver (critical).\n3. Check input source on monitor.",
                "internal_notes": "Source: https://support.displaylink.com/knowledgebase/articles/525121-display-not-working-or-goes-blank",
                "status": Article.Status.APPROVED
            },
            {
                "title": "WAVLINK Dock: USB Ports or Ethernet Not Working",
                "category": Article.Category.HARDWARE,
                "subcategory": "Monitors & Docking Stations",
                "problem": "Internet/Mouse via dock not working.",
                "solution": "1. Re-plug USB-C.\n2. Power cycle dock.\n3. Re-install DisplayLink driver.",
                "internal_notes": "Hub connectivity.",
                "status": Article.Status.APPROVED
            },
            {
                "title": "Windows: How to Change Monitor Arrangement",
                "category": Article.Category.HARDWARE,
                "subcategory": "Monitors & Docking Stations",
                "problem": "Mouse moves to wrong screen.",
                "solution": "1. Right-click Desktop > Display Settings.\n2. Click Identify.\n3. Drag boxes to match physical desk layout.\n4. Apply.",
                "internal_notes": "Source: https://support.microsoft.com/en-us/windows/set-up-dual-monitors-in-windows-3d5c15dc-cc61-d850-aeb0-b419e481b79fff",
                "status": Article.Status.APPROVED
            },
            {
                "title": "Windows: How to Fix Blurry Text on Monitors (ClearType)",
                "category": Article.Category.HARDWARE,
                "subcategory": "Monitors & Docking Stations",
                "problem": "Text looks fuzzy.",
                "solution": "1. Start > Adjust ClearType text.\n2. Follow wizard to pick clearest text.\n3. Check Monitor sharpness settings (set to 50%).",
                "internal_notes": "Source: https://support.microsoft.com/en-us/windows/use-cleartype-in-windows-11-to-make-text-sharper-7d728dae-4a11-4894-814b-253c070932c0",
                "status": Article.Status.APPROVED
            },
            {
                "title": "Monitor: No Signal or 'Input Not Supported' Error",
                "category": Article.Category.HARDWARE,
                "subcategory": "Monitors & Docking Stations",
                "problem": "Screen black or error message.",
                "solution": "No Signal: Check cables, cycle Input button.\nInput Not Supported: PC sending wrong resolution. Boot in safe mode or low res mode to fix refresh rate (60Hz).",
                "internal_notes": "Resolution mismatch.",
                "status": Article.Status.APPROVED
            },
            {
                "title": "Mobile Device: How to Set Up Company Email (Outlook App)",
                "category": Article.Category.HARDWARE,
                "subcategory": "Mobile Devices (iPhones, iPads)",
                "problem": "User needs email on phone.",
                "solution": "1. Download Microsoft Outlook app (Native Mail not supported).\n2. Add Account: user@primeeng.com.\n3. Authenticate with MFA.\nRationale: Security/Selective Wipe capability.",
                "internal_notes": "Source: https://support.microsoft.com/en-us/office/set-up-email-in-the-outlook-for-android-app-886db551-8dfa-4fd5-b835-f8e53609eFF1",
                "status": Article.Status.APPROVED
            },
            {
                "title": "Mobile Device: How to Fix Outlook App Sync Issues",
                "category": Article.Category.HARDWARE,
                "subcategory": "Mobile Devices (iPhones, iPads)",
                "problem": "Email not updating on phone.",
                "solution": "1. Open Outlook Settings > Select Account > Reset Account (Best fix).\n2. Force quit app.",
                "internal_notes": "Source: https://support.microsoft.com/en-us/office/how-can-i-troubleshoot-sync-issues-with-the-outlook-for-android-app-672e3795-c1e1-450f-a492-c4e9d5696174",
                "status": Article.Status.APPROVED
            },
            {
                "title": "Conference Room: How to Connect a Laptop to the TV/Display",
                "category": Article.Category.HARDWARE,
                "subcategory": "Conference Room AV",
                "problem": "Presenting laptop to TV.",
                "solution": "1. Plug in HDMI cable.\n2. Set TV Input to correct HDMI source.\n3. Win+P > Duplicate.",
                "internal_notes": "AV instructions.",
                "status": Article.Status.APPROVED
            },
            {
                "title": "Conference Room: No Audio in Teams/Zoom Call",
                "category": Article.Category.HARDWARE,
                "subcategory": "Conference Room AV",
                "problem": "Can't hear/be heard in conf room.",
                "solution": "1. Teams Settings > Devices.\n2. Change Speaker/Mic from 'Laptop' to 'Room System' or 'Echo Cancelling Speakerphone'.",
                "internal_notes": "Source: https://support.microsoft.com/en-us/office/manage-your-call-settings-in-microsoft-teams-911D551B-EAF3-4B07-88F8-88F23631A91B",
                "status": Article.Status.APPROVED
            },
            {
                "title": "3D Mouse: 3Dconnexion SpaceMouse Not Working in 3ds Max",
                "category": Article.Category.HARDWARE,
                "subcategory": "Specialty Peripherals (3Dconnexion mouse, etc.)",
                "problem": "Puck not working in 3ds Max.",
                "solution": "1. Check Max Customize > Preferences > 3Dconnexion tab (enable if missing).\n2. Re-install 3DxWare driver while Max is CLOSED.",
                "internal_notes": "Source: https://3dconnexion.com/us/support/faq/my-3dconnexion-mouse-is-not-working-in-my-application-after-i-updated-it/",
                "status": Article.Status.APPROVED
            }
        ]

        count = 0
        for data in articles:
            Article.objects.create(**data)
            count += 1
            
        self.stdout.write(self.style.SUCCESS(f"SUCCESS: {count} Articles Published."))