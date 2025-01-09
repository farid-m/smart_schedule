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
    document.getElementById("send-sms").onclick = sendSms; // New button handler
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

async function sendSms() {
  try {
    Office.context.document.getSelectedTaskAsync((result) => {
      if (result.status === Office.AsyncResultStatus.Succeeded) {
        const taskGuid = result.value;

        // Get task properties, including the Notes field (phone number)
        Office.context.document.getTaskFieldAsync(taskGuid, Office.ProjectTaskFields["Number1"], async (taskResult) => {
          if (taskResult.status === Office.AsyncResultStatus.Succeeded) {
            const notesValue = taskResult.value.fieldValue; // Extract phone number from Notes field

            const smsPayload = {
              task: "Building Foundation",
              to_number: notesValue
            };

            try {
              // Send the SMS
              const response = await fetch("http://localhost:5000/interact", {
                method: "POST",
                headers: {
                  "Content-Type": "application/json"
                },
                body: JSON.stringify(smsPayload)
              });

              // Handle the response
              if (response.ok) {
                const result = await response.json(); // Parse JSON response
                console.log("SMS sent successfully:", result);

                if (result.status === "success" && result.summary) {
                  const completionText = result.summary;

                  // Update the Notes field with the completion text
                  Office.context.document.setTaskFieldAsync(
                    taskGuid,
                    Office.ProjectTaskFields.Notes,
                    completionText, // Use the completion text as the Notes content
                    (updateResult) => {
                      if (updateResult.status === Office.AsyncResultStatus.Succeeded) {
                        console.log("Notes field updated successfully with completion text.");
                        alert("Notes field updated successfully!");
                      } else {
                        console.error("Error updating Notes field:", updateResult.error);
                      }
                    }
                  );
                } else {
                  console.error("Unexpected response format or missing summary:", result);
                  alert("Failed to update Notes field due to unexpected response.");
                }
              } else {
                const errorDetails = await response.text();
                console.error("Error sending SMS:", errorDetails);
                alert("Failed to send SMS. Check the console for details.");
              }
            } catch (fetchError) {
              console.error("Error during SMS sending process:", fetchError);
              alert("Failed to send SMS due to network issues.");
            }
          } else {
            console.error("Error retrieving task properties:", taskResult.error);
          }
        });
      } else {
        console.error("Error retrieving selected task:", result.error);
      }
    });
  } catch (error) {
    console.error("Unexpected error:", error);
    alert("An error occurred. Check the console for details.");
  }
}

