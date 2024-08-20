import json
import os
import logging

from satisfactoryobjects import itemhandler, recipehandler, machinehandler, nativeclasses

toplevel_logger = logging.getLogger(__name__)

SATISFACTORY_ROOT = os.path.expanduser("~/.local/share/Steam/steamapps/common/Satisfactory/")
SATISFACTORY_DOCS = "CommunityResources/Docs/Docs.json"


def main():
    logger = toplevel_logger.getChild("main")

    logger.debug("Begin registering native class handlers")

    nativeclasses.SatisfactoryNativeClassHandler(
        "/Script/CoreUObject.Class'/Script/FactoryGame.FGRecipe'",
        recipehandler.handler,
        defer_pass=10
    )

    nativeclasses.SatisfactoryNativeClassHandler(
        "/Script/CoreUObject.Class'/Script/FactoryGame.FGBuildableManufacturer'",
        machinehandler.fixed_power_machine_handler
    )

    nativeclasses.SatisfactoryNativeClassHandler(
        "/Script/CoreUObject.Class'/Script/FactoryGame.FGBuildableManufacturerVariablePower'",
        machinehandler.variable_power_machine_handler
    )

    # TODO: maybe this first one should be a different handler which saves to a different list?
    nativeclasses.SatisfactoryNativeClassHandler(
        "/Script/CoreUObject.Class'/Script/FactoryGame.FGResourceDescriptor'",
        itemhandler.handler
    )

    nativeclasses.SatisfactoryNativeClassHandler(
        "/Script/CoreUObject.Class'/Script/FactoryGame.FGItemDescriptor'",
        itemhandler.handler
    )

    # TODO: maybe these should be derived classes?
    nativeclasses.SatisfactoryNativeClassHandler(
        "/Script/CoreUObject.Class'/Script/FactoryGame.FGItemDescriptorNuclearFuel'",
        itemhandler.handler
    )
    nativeclasses.SatisfactoryNativeClassHandler(
        "/Script/CoreUObject.Class'/Script/FactoryGame.FGItemDescriptorBiomass'",
        itemhandler.handler
    )

    logger.info(f"Satisfactory installation root determined as {SATISFACTORY_ROOT}")

    satisfactory_docs_absolute_path = os.path.join(SATISFACTORY_ROOT, SATISFACTORY_DOCS)

    logger.debug(f"Opening documentation file {satisfactory_docs_absolute_path}")
    with open(satisfactory_docs_absolute_path, "r", encoding="UTF-16") as fptr:
        logger.debug("Deserialising documentation data")
        dat = json.load(fptr)
        logger.debug("Loading documentation data")
        for obj in dat:
            # if obj["NativeClass"] == "/Script/CoreUObject.Class'/Script/FactoryGame.FGItemDescriptor'":
            # subtypes = obj["Classes"]
            # for c in subtypes:
            # 	print(c["ClassName"])

            # add the handlers to a priority queue
            nativeclasses.SatisfactoryNativeClassHandler.enqueue_handle(obj)
        logger.debug("Finished preparing documentation data load")
        # dequeue all the handlers in order
        nativeclasses.SatisfactoryNativeClassHandler.handle()

    print([item.user_facing_name for _, item in itemhandler.items.items()])
    print([recipe.user_facing_name for _, recipe in recipehandler.recipes.items()])
    print([recipe.calcPowerFlowRate() for _, recipe in recipehandler.recipes.items()])


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, filename="last.log", filemode="w")
    toplevel_logger.info("Set log configuration")
    main()
