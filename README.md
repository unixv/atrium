# Atrium Alpha

Atrium is a small websocket multiplayer room prototype with Mongo-backed accounts, spaces, avatars, and placed room items.

## Run locally

Install Docker with the Compose plugin, then from the repository root run:

```bash
make dev
```

Compose builds the frontend and backend and starts MongoDB. Open http://localhost:5173.
Stop with Ctrl+C, or run `make down` in another terminal. For a local
frontend build without Docker, install Node.js and npm; backend checks need Python 3.10+.

Click a floor tile to walk, or use the arrow keys/WASD. Keyboard movement is
paused while typing in chat or another form and while arranging furniture.

## Useful commands

```bash
make check      # frontend tests, typecheck, build + backend compile
PYTHONPATH=backend python -m unittest discover -s backend/tests  # backend unit tests
make logs       # stream docker logs
make down       # stop containers
make clean      # remove generated local caches
```

## Project map

```text
backend/atrium/
  app.py                         websocket app + Mongo-backed spaces/items
  auth.py                        login/register/token helpers
  client.py                      connected player state
  world.py                       available room layouts
  models/
    avatar.py                    avatar fields and validation
    item_catalog.py              canonical build catalog and sprite metadata
  commands/
    auth/                        auth.login, auth.register, auth.resume
    avatar/                      avatar.update
    communication/               message.send
    items/                       inventory.list, item.place, item.remove, item.use, items.clear
    movement/                    position.walk
    spaces/                      space create/list/join/update

frontend/src/
  game/
    roomRenderer.ts              isometric room, item, player, and bubble rendering
    characterSprite.ts           customizable pixel character renderer
    movement.ts                  click-to-walk and build click handling
    worldLayout.ts               frontend layout validation helpers
    spriteImages.ts              cached image loader
  features/
    characterEditor.ts           avatar builder UI
    inventory.ts                 design/catalog UI
  ui/
    auth.ts, chat.ts, members.ts, spaces.ts
```

## Mongo collections

```text
users        accounts and avatar data
spaces       rooms, owners, descriptions, layout_id
space_items  placed room items
```

## Adding a room layout

Add an entry to `backend/atrium/world.py`. Spaces store only `layout_id`, so changing a layout updates every space using it.

## Adding an item

1. Put a transparent PNG in `frontend/public/assets/items/`.
2. Add metadata in `backend/atrium/models/item_catalog.py`.
3. Run `make check`.

Important catalog fields:

```python
item("id", "Name", "Category", "png_name", width, height,
     draw_width_tiles=1.2,
     anchor_tile_y=0.90,
     can_sit=True,
     seat={"x": 0, "y": 0})
```

## Avatar customization

Avatar customization is part-based, not preset-only. The backend stores:

```text
avatar_preset  body/profile shape
skin_color
hair_style
hair_color
shirt_style
shirt_color
pants_style
pants_color
shoe_style
shoe_color
```

The frontend renders those fields into a pixel character in `characterSprite.ts`.
