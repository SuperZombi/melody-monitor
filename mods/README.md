# Mods for Melody Monitor

### How to install mod
1. Download desired mod file.
2. Move archive to `mods` folder.
3. To configure the mod, go to the program settings (in tray).

### How to create mod
1. Create a new folder inside `mods` folder.
2. Create a `meta.json` file.
```
{
  "id": "mod_id",
  "name": "Mod Name",
  "author": "Mod Author",
  "description": "Mod Description",
  "icon": "https://icon_url",
  "files": ["main.css"]
}
```
3. Create a `.css` file that you specified in config.
4. Pack your files into .zip archive (optional).