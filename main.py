import json
import logging
import argparse
import pathlib
import sys

from satisfactoryobjects import (
    itemhandler,
    recipehandler,
    machinehandler,
    nativeclasses,
    recipelookup
)

toplevel_logger = logging.getLogger(__name__)


def get_default_satisfactory_docs_path() -> pathlib.Path | None:
    # think this is the same for all satisfactory installations
    SATISFACTORY_DOCS = pathlib.Path('CommunityResources/Docs/Docs.json')
    # also if you are reading this and have the time and it is after my nea
    # deadline and have satisfactory on eric james launcher i would appreciate
    # it if you checked where it plonked satisfactory, so i can add it as an
    # option (or you could make a pr)
    # i only have satisfactory on steam
    # also if you have the eric james version and use linux could you maybe
    # test with heroic games launcher and/or lutris-installed eric james
    # launcher (or some other launcher i havent heard of)
    match sys.platform:
        case 'emscripten' | 'wasi':
            # webassembly
            # probably wont work well, if at all
            return None
        case 'android':
            # i think qt for python lets you build android apps but i dont
            # know how open() would work there (probably not at all with SAF)
            # this app may work there but isnt really designed for it.
            # try this one at your own risk.
            return None
        case 'ios':
            # does qt for python even support ios?
            # would probably be hell to get working even if you do pay the
            # recurring developer ransom
            return None
        case 'linux':
            # best tested platform.
            return pathlib.PosixPath(
                "~/.local/share/Steam/steamapps/common/Satisfactory/"
            ).expanduser().joinpath(SATISFACTORY_DOCS).resolve()
        case 'win32' | 'cygwin':
            # all windows
            # i think cygwin lets you access windows paths directly
            # windows is the only platform satisfactory itself officially
            # supports
            # TODO: check where the file is on Windows
            return None
        case 'darwin':
            # macos (darwin bsd)
            # official support not planned but should work
            # feel free to add the path here and pull request
            # from whenever my nea deadline has passed
            # (idk lets say june 2025 will definitely be passed)
            return None
        case 'aix':
            # likely would work decently if the docs file was provided
            # but i doubt steam supports this platform
            return None
        case _:
            # default pattern i.e. OS not in python documentation as of writing
            return None


def register_handlers() -> None:
    """Register the native class handlers used to load the required data.
    WARNING: inadvisible to call this more than once"""
    logger = toplevel_logger.getChild("register_handlers")

    logger.debug("Begin registering native class handlers")

    nativeclasses.SatisfactoryNativeClassHandler(
        (
            "/Script/CoreUObject.Class'"
            "/Script/FactoryGame.FGRecipe'"
        ),
        recipehandler.handler,
        defer_pass=10
    )

    nativeclasses.SatisfactoryNativeClassHandler(
        (
            "/Script/CoreUObject.Class'"
            "/Script/FactoryGame.FGBuildableManufacturer'"
        ),
        machinehandler.fixed_power_machine_handler
    )

    nativeclasses.SatisfactoryNativeClassHandler(
        (
            "/Script/CoreUObject.Class'"
            "/Script/FactoryGame.FGBuildableManufacturerVariablePower'"
        ),
        machinehandler.variable_power_machine_handler
    )

    # TODO: maybe this first one should be a different handler which saves to
    # a different list?
    nativeclasses.SatisfactoryNativeClassHandler(
        (
            "/Script/CoreUObject.Class'"
            "/Script/FactoryGame.FGResourceDescriptor'"
        ),
        itemhandler.handler
    )

    nativeclasses.SatisfactoryNativeClassHandler(
        (
            "/Script/CoreUObject.Class'"
            "/Script/FactoryGame.FGItemDescriptor'"
        ),
        itemhandler.handler
    )

    # TODO: maybe these should be derived classes?
    nativeclasses.SatisfactoryNativeClassHandler(
        (
            "/Script/CoreUObject.Class'"
            "/Script/FactoryGame.FGItemDescriptorNuclearFuel'"
        ),
        itemhandler.handler
    )
    nativeclasses.SatisfactoryNativeClassHandler(
        (
            "/Script/CoreUObject.Class'"
            "/Script/FactoryGame.FGItemDescriptorBiomass'"
        ),
        itemhandler.handler
    )

    logger.debug("Finished registering native class handlers")


def load_docs(satisfactory_docs_absolute_path: pathlib.Path) -> None:
    """Load Docs.json at the given path and trigger handlers
    WARNING: Inadvisable to call this more than once."""
    logger = toplevel_logger.getChild("load_docs")

    logger.debug(
        f"Opening documentation file {satisfactory_docs_absolute_path}"
    )
    with open(satisfactory_docs_absolute_path, "r", encoding="UTF-16") as fptr:
        logger.debug("Deserialising documentation data")
        dat = json.load(fptr)
        logger.debug("Loading documentation data")
        for obj in dat:
            # add the handlers to a priority queue
            nativeclasses.SatisfactoryNativeClassHandler.enqueue_handle(obj)
        logger.debug("Finished preparing documentation data load")
        # dequeue all the handlers in order
        nativeclasses.SatisfactoryNativeClassHandler.handle()


def main(arguments: argparse.Namespace):
    logger = toplevel_logger.getChild("main")

    if arguments.docs_file is None:
        logger.critical(
            'Satisfactory docs path could not be autodetermined and was not \
                provided!'
        )
        # see /usr/include/sysexits.h on your linux system for more info
        sys.exit(64)
    logger.info(
        f'Satisfactory docs path to use is {arguments.docs_file}'
    )

    register_handlers()

    load_docs(arguments.docs_file)

    print(
        [
            item
            for _, item
            in itemhandler.items.items()
        ]
    )
    print(
        [
            recipe
            for _, recipe
            in recipehandler.recipes.items()
        ]
    )
    print(
        [
            recipe.calcPowerFlowRate()
            for _, recipe
            in recipehandler.recipes.items()
        ]
    )

    print(
        [
            recipe
            for recipe
            in recipelookup.lookup_recipes(
                itemhandler.items["Desc_IronPlate_C"]
            )
        ]
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog='Satisfactory Optimiser',
        description='Linear programming solver for Satisfactory item \
            production'
    )

    # path to docs file
    # see
    # https://dusty.phillips.codes/2018/08/13/python-loading-pathlib-paths-with-argparse/
    parser.add_argument(
        '-d', '--docs-file',
        action='store',
        type=pathlib.Path,
        default=get_default_satisfactory_docs_path()
    )

    # log level verbosity
    # default is equivalent to warnings and above
    parser.add_argument(
        '-v', '--verbose',
        action='count',
        default=0,
    )

    parser.add_argument(
        '-q', '--quiet',
        action='count',
        default=0
    )

    passed_arguments = parser.parse_args()

    # parse and validate log level args
    # dictionary key is n of verbose then n of quiet
    _LOG_LEVELS: dict = {
        (2, 0): logging.DEBUG,
        (1, 0): logging.INFO,
        (0, 0): logging.WARNING,
        (0, 1): logging.ERROR,
        (0, 2): logging.CRITICAL
    }
    _configured_log_level = logging.NOTSET
    try:
        _configured_log_level = _LOG_LEVELS[
            # min() calls to maintain conventional verbosity argument
            # behaviour (i.e. any past n will have no effect)
            (
                min(passed_arguments.verbose, 2),
                min(passed_arguments.quiet, 2)
            )
        ]
    except KeyError:
        raise ValueError(
            "Invalid log verbosity.  Cannot specify both quietness and \
                verbosity simultaneously."
        )

    logging.basicConfig(
        level=_configured_log_level,
        filename="last.log",
        filemode="w"
    )
    toplevel_logger.debug("Early init done (logging configured).")
    toplevel_logger.debug(
        "Errors should now be loggable in addition to panic/ignore"
    )

    main(passed_arguments)
