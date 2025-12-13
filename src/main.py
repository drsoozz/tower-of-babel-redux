import traceback

import tcod

import color
import consts
import exceptions
import input_handlers
import setup_game


def save_game(handler: input_handlers.BaseEventHandler, filename: str) -> None:
    """If the current event handler has an active Engine then save it."""
    if isinstance(handler, input_handlers.EventHandler):
        handler.engine.save_as(filename)
        print("Game saved.")


def main() -> None:

    # load the font
    tileset = tcod.tileset.load_tilesheet(
        consts.TILESET_PATH, 16, 16, tcod.tileset.CHARMAP_CP437
    )

    handler: input_handlers.BaseEventHandler = setup_game.MainMenu()

    with tcod.context.new(
        columns=consts.SCREEN_WIDTH,
        rows=consts.SCREEN_HEIGHT,
        tileset=tileset,
        title="Tower of Babel",
        vsync=True,
    ) as context:
        root_console = tcod.console.Console(
            width=consts.SCREEN_WIDTH, height=consts.SCREEN_HEIGHT, order="F"
        )
        try:
            while True:
                root_console.clear()
                handler.on_render(console=root_console)
                context.present(root_console)

                try:
                    if isinstance(handler, input_handlers.LoopHandler):
                        handler = handle_wait_handler(handler, context, root_console)
                        continue
                    for event in tcod.event.wait():
                        context.convert_event(
                            event
                        )  # mouse pixel coords into tile coords
                        if isinstance(handler, input_handlers.EventHandler):
                            # pylint: disable-next=unexpected-keyword-arg
                            handler = handler.handle_events(event, root_console)
                        else:
                            handler = handler.handle_events(event)
                except exceptions.QuitToMainMenu:
                    save_game(handler, "savegame.sav")
                    handler = setup_game.MainMenu()
                except Exception:  # Handle exceptions in game.
                    traceback.print_exc()  # Print error to stderr.
                    # Then print the error to the message log.
                    if isinstance(handler, input_handlers.EventHandler):
                        handler.engine.message_log.add_message(
                            traceback.format_exc(), color.error.rgb
                        )
        except exceptions.QuitWithoutSaving:
            raise
        except SystemExit:  # Save and quit.
            save_game(handler, "savegame.sav")
            raise
        except BaseException:  # Save on any other unexpected exception.
            save_game(handler, "savegame.sav")
            raise


def handle_wait_handler(
    handler: input_handlers.LoopHandler,
    context: tcod.context.Context,
    console: tcod.console.Console,
):
    # collect user input, if any
    events = tcod.event.get()

    for event in events:
        context.convert_event(event)
        new_handler = handler.handle_events(event, console)
        if new_handler is not handler:
            # wait was cancelled
            return new_handler

    # execute one rest tick
    new_handler = handler.tick(console)

    return new_handler


if __name__ == "__main__":
    main()
