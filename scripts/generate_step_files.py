#!/usr/bin/freecadcmd

import os
import shutil
import subprocess
import FreeCAD as App  # type: ignore
import Mesh  # type: ignore

project_root = os.path.abspath(
    os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir)
)

printed_cad_dir = os.path.join(project_root, "printed")
printed_out_dir = os.path.join(project_root, "step")

if os.path.exists(printed_out_dir):
    shutil.rmtree(printed_out_dir, ignore_errors=True)

os.makedirs(printed_out_dir, exist_ok=True)

failed_files = []

for root, dirs, files in os.walk(printed_cad_dir):
    for file in files:
        if file.endswith(".FCStd"):
            file_path = os.path.join(root, file)

            App.Console.PrintMessage(f"\nProcessing {file_path}\n")

            doc = App.openDocument(file_path)
            App.setActiveDocument(doc.Name)
            App.ActiveDocument.recompute()

            for obj in doc.Objects:
                if obj.TypeId == "App::Part":
                    output_path = os.path.join(
                        printed_out_dir,
                        os.path.relpath(root, printed_cad_dir),
                        f"{obj.Label}.step",
                    )
                    os.makedirs(os.path.dirname(output_path), exist_ok=True)

                    try:
                        obj.Shape.exportStep(output_path)
                        App.Console.PrintMessage(
                            f"Exported {obj.Label} to {output_path}\n"
                        )
                    except Exception as e:
                        App.Console.PrintError(f"Error exporting {obj.Label}: {e}\n")
                        failed_files.append(file_path)

            App.closeDocument(doc.Name)

if failed_files:
    App.Console.PrintError("\nThe following files failed to export:\n")
    for file in failed_files:
        App.Console.PrintError(f" - {file}\n")
else:
    App.Console.PrintMessage("\nAll files have been exported successfully.\n")
