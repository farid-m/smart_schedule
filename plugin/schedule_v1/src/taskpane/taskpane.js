/*
 * Copyright (c) Microsoft Corporation. All rights reserved. Licensed under the MIT license.
 * See LICENSE in the project root for license information.
 */

/* global console document, Office */

Office.onReady((info) => {
  if (info.host === Office.HostType.Project) {
    document.getElementById("sideload-msg").style.display = "none";
    document.getElementById("app-body").style.display = "flex";
    document.getElementById("retrieve").onclick = retrieve;
    document.getElementById("send-sms").onclick = sendSms; // New button handler
  }
});

async function retrieve() {
  Office.context.document.getSelectedTaskAsync((result) => {
    if (result.status === Office.AsyncResultStatus.Succeeded) {
      const taskGuid = result.value;

      try {
        const smsPayload = {
          taskguid: taskGuid // Corrected variable name
        };

        // Function to handle fetch logic
        (async () => {
          try {
            const response = await fetch("http://localhost:5000/retrieve", {
              method: "POST",
              headers: {
                "Content-Type": "application/json"
              },
              body: JSON.stringify(smsPayload)
            });

            if (response.ok) {
              const result = await response.json(); // Parse JSON response
              console.log("Request successful:", result);

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
              console.error("Error in API response:", errorDetails);
              alert("API request failed. Check the console for details.");
            }
          } catch (fetchError) {
            console.error("Error during API request:", fetchError);
            alert("Failed to send request due to network issues.");
          }
        })();
      } catch (error) {
        console.error("Unexpected error:", error);
        alert("An error occurred while preparing the API request.");
      }
    } else {
      console.error("Error retrieving selected task:", result.error);
      alert("Failed to retrieve the selected task. Check the console for details.");
    }
  });
}
async function sendSms() {
  try {
    Office.context.document.getSelectedTaskAsync((result) => {
      if (result.status === Office.AsyncResultStatus.Succeeded) {
        const taskGuid = result.value;

        // Get task properties, including the Notes field (phone number)
        Office.context.document.getTaskFieldAsync(taskGuid, Office.ProjectTaskFields["Number1"], (taskResult) => {
          if (taskResult.status === Office.AsyncResultStatus.Succeeded) {
            const notesValue = taskResult.value.fieldValue; // Extract phone number from the "Number1" field

            // Retrieve the Task Name field
            Office.context.document.getTaskAsync(taskGuid, (taskNameResult) => {
              if (taskNameResult.status === Office.AsyncResultStatus.Succeeded) {
                const taskName = taskNameResult.value.taskName; // Extract the task name

                const smsPayload = {
                  task: taskName, // Use the dynamically retrieved Task Name
                  to_number: notesValue,
                  taskguid: taskGuid
                };

                // Send the SMS (fire-and-forget approach)
                fetch("http://localhost:5000/interact", {
                  method: "POST",
                  headers: {
                    "Content-Type": "application/json"
                  },
                  body: JSON.stringify(smsPayload)
                }).catch((error) => {
                  console.error("Error during SMS sending process:", error);
                  alert("Failed to send SMS due to network issues.");
                });

                console.log("SMS request sent. No need to wait for the response.");
              } else {
                console.error("Error retrieving Task Name field:", taskNameResult.error);
                alert("Failed to retrieve the Task Name field. Check the console for details.");
              }
            });
          } else {
            console.error("Error retrieving Number1 field:", taskResult.error);
            alert("Failed to retrieve the Number1 field. Check the console for details.");
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

