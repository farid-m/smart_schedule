/*
 * Copyright (c) Microsoft Corporation. All rights reserved. Licensed under the MIT license.
 * See LICENSE in the project root for license information.
 */

/* global console document, Office */

Office.onReady((info) => {
  if (info.host === Office.HostType.Project) {
    document.getElementById("sideload-msg").style.display = "none";
    document.getElementById("app-body").style.display = "flex";
    document.getElementById("run").onclick = run;
  }
});

export async function run() {
  try {
    // Get the GUID of the selected task
    Office.context.document.getSelectedTaskAsync((result) => {
      if (result.status === Office.AsyncResultStatus.Succeeded) {
        const taskGuid = result.value;

        // Get task properties, including the task name
        Office.context.document.getTaskAsync(taskGuid, (taskResult) => {
          if (taskResult.status === Office.AsyncResultStatus.Succeeded) {
            const taskName = taskResult.value.taskName; // Retrieve the current task name
            const notesFieldContent = `Task name is: ${taskName}`; // Format the string for Notes field

            // Update the Notes field with the task name
            Office.context.document.setTaskFieldAsync(
              taskGuid,
              Office.ProjectTaskFields.Notes,
              notesFieldContent,
              (updateResult) => {
                if (updateResult.status === Office.AsyncResultStatus.Succeeded) {
                  console.log("Notes field updated successfully.");
                } else {
                  console.error(updateResult.error);
                }
              }
            );
          } else {
            console.error(taskResult.error);
          }
        });
      } else {
        console.error(result.error);
      }
    });
  } catch (error) {
    console.error(error);
  }
}
