#!/usr/bin/env -S PYTHONHASHSEED=0 python3
# The -S means "split string" i.e. if it is part of one element of argv then
# break that argument into separate arguments on spaces.  This is required if
# passing multiple arguments in a shebang, since Linux will pass everything
# past the first space in the shebang as a single argument to the program.
# -S isn't exactly portable (it is available from GNU coreutils 8.30) but it
# has worked on both systems that I tried it on.
import json
import logging
import pathlib
import os
import sys

# PySide6 dependency here to parse arguments
# (because argparse has too many limitations to use alongside)
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QCommandLineOption, QCommandLineParser

from gui.window import MainWindow

from satisfactoryobjects import (
    itemhandler,
    recipehandler,
    machinehandler,
    nativeclasses
)

VALID_LOG_VERBOSITY_LEVELS = {
    'debug': logging.DEBUG,
    'info': logging.INFO,
    'warn': logging.WARNING,
    'error': logging.ERROR,
    'crit': logging.CRITICAL
}

toplevel_logger = logging.getLogger(__name__)


def get_default_satisfactory_docs_path() -> pathlib.Path | None:
    # think this is the same for all satisfactory installations
    # TODO: allow passing the locale as an argument or try and autodetermine it
    # from the system config?  since post-1.0 it changed to have multiple
    # versions per-locale
    # TODO: autodetect if the old docs path is present, and if so use it
    # TODO: try a few possible different docs root paths (e.g. steam, then
    # epic games on windows/mac, then heroic on mac/linux, then epic games via
    # lutris on linux) - will probably not get done due to not owning the game
    # on epic myself and not really having time to borrow a macbook to test
    # steam on macos
    # OLD_SATISFACTORY_DOCS = pathlib.Path('CommunityResources/Docs/Docs.json')
    SATISFACTORY_DOCS = pathlib.Path('CommunityResources/Docs/en-GB.json')
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
                '~/.local/share/Steam/steamapps/common/Satisfactory/'
            ).expanduser().joinpath(SATISFACTORY_DOCS).resolve()
        case 'win32' | 'cygwin':
            # all windows
            # i think cygwin lets you access windows paths directly
            # windows is the only platform satisfactory itself officially
            # supports
            # TODO: check if a PosixPath is required under cygwin (pathlib
            # will refuse to instantiate a WindowsPath on a posix system and
            # vice versa)
            return pathlib.WindowsPath(
                'C:/Program Files (x86)/Steam/steamapps/common/Satisfactory/'
            ).joinpath(SATISFACTORY_DOCS).resolve()
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


def parse_arguments(app: QApplication) -> tuple[pathlib.Path, int]:
    # code based off of examples at
    # https://www.pythonguis.com/faq/command-line-arguments-pyqt6/
    parser = QCommandLineParser()
    parser.addHelpOption()
    parser.addVersionOption()

    suggested_default_path = get_default_satisfactory_docs_path()

    file_path_option = QCommandLineOption(
        'p',
        'Path to Docs.json',
        'path'
    )

    if suggested_default_path is not None:
        file_path_option.setDefaultValue(str(suggested_default_path))
    parser.addOption(file_path_option)

    verbosity_level_option = QCommandLineOption(
        'l',
        'Log verbosity level (one of '
        f'{", ".join([lvl for lvl in VALID_LOG_VERBOSITY_LEVELS])})',
        'verbosity',
        'warn'
    )
    parser.addOption(verbosity_level_option)

    parser.process(app)

    used_path = parser.value(file_path_option)
    raw_verbosity_level = parser.value(verbosity_level_option)
    verbosity_level = logging.NOTSET

    if suggested_default_path is None and not used_path:
        raise ValueError(
            'Path could not be autodetermined and was not specified!'
        )
    try:
        verbosity_level = VALID_LOG_VERBOSITY_LEVELS[
            raw_verbosity_level.lower()
        ]
    except KeyError:
        raise ValueError('Invalid log verbosity level!')

    return (pathlib.Path(used_path).expanduser().resolve(), verbosity_level)


def register_handlers() -> None:
    '''Register the native class handlers used to load the required data.
    WARNING: inadvisible to call this more than once
    '''
    logger = toplevel_logger.getChild('register_handlers')

    logger.debug('Begin registering native class handlers')

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

    logger.debug('Finished registering native class handlers')


def load_docs(satisfactory_docs_absolute_path: pathlib.Path) -> None:
    '''Load Docs.json at the given path and trigger handlers
    WARNING: Inadvisable to call this more than once.
    '''
    logger = toplevel_logger.getChild('load_docs')

    logger.debug(
        f'Opening documentation file {satisfactory_docs_absolute_path}'
    )
    with open(satisfactory_docs_absolute_path, 'r', encoding='UTF-16') as fptr:
        logger.debug('Deserialising documentation data')
        dat = json.load(fptr)
        logger.debug('Loading documentation data')
        for obj in dat:
            # add the handlers to a priority queue
            nativeclasses.SatisfactoryNativeClassHandler.enqueue_handle(obj)
        logger.debug('Finished preparing documentation data load')
        # dequeue all the handlers in order
        nativeclasses.SatisfactoryNativeClassHandler.handle()


def main(
    configured_docs_path: pathlib.Path,
    qt_application: QApplication
) -> int:
    logger = toplevel_logger.getChild('main')

    logger.info(
        f'Satisfactory docs path to use is {configured_docs_path}'
    )

    register_handlers()

    load_docs(configured_docs_path)

    # gui init

    main_window = MainWindow(qt_application)
    main_window.show()

    # start up qt application event loop and return its return code
    return qt_application.exec()


if __name__ == '__main__':
    # make the program deterministic
    # cannot have logging yet since we are substituting the entire process
    # without cleaning up file handles etc
    if sys.flags.hash_randomization:
        try:
            if os.environ[
                'io.github.bartlett-m.INTERNALEXPECTHASHRANDOMISATIONOFF'
            ] == '1':
                print(
                    'Hash randomisation should have been automatically '
                    'disabled, but it is not!'
                )
                print(
                    'Please relaunch the program without giving python the -R '
                    'argument!'
                )
            else:
                print(
                    'Internal environment variable used for state has corrupt '
                    'value!'
                )
                print(
                    'Please unset the following environment variable:'
                )
                print(
                    'io.github.bartlett-m.INTERNALEXPECTHASHRANDOMISATIONOFF'
                )
            print('CRITICAL EARLY ERROR, CANNOT CONTINUE')
            print('HASH_RANDOMISATION_DISABLEMENT_FAILED')
            # if we got to this line, this internal environment variable was
            # either already set outside the program or python was started
            # with -R
            sys.exit(78)
        except KeyError:
            # not set, as expected
            pass
        # turn off hash randomisation
        os.environ['PYTHONHASHSEED'] = '0'
        # tell the program to expect hash randomisation to be turned off (so we
        # dont enter an infinite loop if python was started with -R, which
        # overrides the environment variable)
        os.environ[
            'io.github.bartlett-m.INTERNALEXPECTHASHRANDOMISATIONOFF'
        ] = '1'
        # The first item from argv is discarded by python3 (since it is
        # normally the interpreter executable).  However, with os.execvp, the
        # args specified are the entire argv, and thus it is possible to start
        # python3 without the interpreter executable being in argv.  Python
        # does not expect this and will then discard our script path.  To fix
        # this, we must pass the entire original argv as the arguments.

        # os.execvp does not work on windows if the executable has spaces in
        # it, and there is no way to escape it.  also we dont get the benefits
        # (same PID etc) of it.  best alternative was to use subprocess.run.
        # however, this has issues (e.g. stdout, stderr are buffered and thus
        # you cant see them until the program is done) so some workarounds
        # need to be performed.
        if sys.platform == 'win32':
            # its bad practice to put imports not at the top of the file, but
            # since this is only used on a specific platform and even then not
            # always its more sensible to not import it if its not needed.
            import subprocess
            # work around aforementioned issue with stdout, stderr being
            # buffered and thus not being shown until program terminates
            os.environ[
                'PYTHONUNBUFFERED'
            ] = '1'  # this can actually be set to any arbitrary string to work

            sys.exit(
                subprocess.run(sys.orig_argv).returncode
            )

        os.execvp(sys.orig_argv[0], sys.orig_argv)

    app = QApplication(sys.argv)
    app.setApplicationName('Satisfactory Optimiser')
    app.setApplicationVersion('1.0.0')
    app.setOrganizationName('bartlett-m')
    app.setOrganizationDomain('bartlett-m.github.io')

    configured_docs_path, configured_log_level = parse_arguments(app)

    logging.basicConfig(
        level=configured_log_level,
        filename='last.log',
        filemode='w'
    )
    toplevel_logger.debug('Early init done (logging configured).')
    toplevel_logger.debug(
        'Errors should now be loggable in addition to panic/ignore'
    )

    # call main program, and exit with the return code it provides
    sys.exit(
        main(configured_docs_path, app)
    )
