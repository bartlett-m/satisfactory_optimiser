import logging
from typing import Type
from utils.queueutils import PrioritisedItem
from queue import PriorityQueue

toplevel_logger = logging.getLogger(__name__)


class SatisfactoryNativeClassHandler:
    logger = toplevel_logger.getChild("SatisfactoryNativeClassHandler")
    handlers: dict[str, Type["SatisfactoryNativeClassHandler"]] = dict()
    _handler_queue: PriorityQueue[PrioritisedItem] = PriorityQueue()

    def __init__(self, class_name, handler_function, defer_pass=0):
        SatisfactoryNativeClassHandler.logger.debug(
            f"Registering new native class handler for class {class_name}"
        )
        self.class_name = class_name
        self._handle = handler_function
        self._defer_pass = defer_pass
        # if self._defer_pass > SatisfactoryNativeClassHandler._max_defer_pass:
        #     SatisfactoryNativeClassHandler._max_defer_pass = defer_pass
        SatisfactoryNativeClassHandler.handlers[class_name] = self

    def enqueue_handle(obj):
        try:
            handler = SatisfactoryNativeClassHandler.handlers[
                obj["NativeClass"]
            ]
            SatisfactoryNativeClassHandler.logger.debug(
                    f"Enqueueing handling of class {obj["NativeClass"]}"
                )
            SatisfactoryNativeClassHandler._handler_queue.put(
                PrioritisedItem(handler._defer_pass, obj)
            )
        except KeyError:
            # no registered handler for class
            SatisfactoryNativeClassHandler.logger.debug(
                f"No handler registered for class {obj["NativeClass"]}"
            )

    def handle() -> None:
        """Execute the enqueued handlers"""
        SatisfactoryNativeClassHandler.logger.info("Running handlers")
        while not SatisfactoryNativeClassHandler._handler_queue.empty():
            obj = SatisfactoryNativeClassHandler._handler_queue.get().item
            handler = SatisfactoryNativeClassHandler.handlers[
                obj["NativeClass"]
            ]
            handler._handle(obj)
            SatisfactoryNativeClassHandler.logger.debug(
                f"Handled class {obj["NativeClass"]}"
            )

    # some test handlers
    def noop(obj):
        """Handler that does nothing"""
        pass

    def log(obj):
        """Handler that logs the object"""
        SatisfactoryNativeClassHandler.logger.debug(obj)


def _log_denamespace_failure(
    namespaced_classname: str,
    debug_message: str
) -> None:
    """Logs a denamespacing failure and throws an exception.
    We repeat: ALWAYS RAISES A ValueError!

    This function provides a code snippet frequently used by the function
    denamespace_satisfactory_classname()
    """
    toplevel_logger.critical(
        f"Cannot denamespace classname {namespaced_classname}"
    )
    toplevel_logger.debug(debug_message)
    raise ValueError("Invalid namespaced satisfactory classname.")


def denamespace_satisfactory_classname(namespaced_classname: str) -> str:
    """Removes the namespace from a classname referenced in docs.json

    The returned classname is the format seemingly used in the referenced
    objects definition, so said objects can be looked up.
    """
    unparsed_namespace, _, unparsed_classname \
        = namespaced_classname.rpartition("/")
    # first - a disclaimer: every time i think i have figured out the rules of
    # this format, an exception to the rule appears, so the following comments
    # will likely contradict each other and the code will be quite messy

    # how the namespaces are dereferenced in docs.json is unclear
    # as they do not seem to be used anywhere by the objects that
    # the namespaced classnames are referencing, or their parents
    # in the json structure.  it therefore appears safe to discard
    # them.

    # all the classes appear to be a subclass (or something) of
    # /Script/Engine.BlueprintGeneratedClass
    # their type/namespace/name/whatever is surrounded by double quotes
    # that are themselves surrounded by single quotes.
    # so '"namespaced/name"' (verbatim)
    # however, sometimes the /Script/Engine.BluprintGeneratedClass does not
    # appear.  in this case, the single and double quotes are also ommitted.

    # the class name is almost always repeated, separated with a '.'
    # the second occurence also has '_C' appended (except some like FGBuildGun
    # and FGBuildableAutomatedWorkbench - FGBuildGun also sounds like a
    # duplicate of BP_BuildGun_C i dont know anymore)
    # the second occurence is how the class is referenced elsewhere
    _parser_temp = unparsed_classname.split('.')
    # check for bad splitting
    if len(_parser_temp) != 2:
        _log_denamespace_failure(
            namespaced_classname,
            f"Partitioned segment {unparsed_classname} "
            f"appears to contain {len(_parser_temp)-1} "
            "occurences of the character '.'"
        )

    # handle added quotes
    if _parser_temp[1][-2:] == '"\'':
        return _parser_temp[1][:-2]

    return _parser_temp[1]
