Usage example
-------------

Model Target datasets
~~~~~~~~~~~~~~~~~~~~~

Model Target dataset commands use OAuth2 credentials for the `Model Target Web API`_, rather than server keys.
Vuforia generates a dataset in the background, so create the dataset, wait for it, and then download it.

.. _Model Target Web API: https://developer.vuforia.com/library/vuforia-engine/web-api/model-target-web-api/

.. skip doccmd[shellcheck]: start

.. code-block:: console

   $ vws create-model-target-dataset \
       --client-id "$MODEL_TARGET_CLIENT_ID" \
       --client-secret "$MODEL_TARGET_CLIENT_SECRET" \
       --name my_dataset_name \
       --target-sdk 10.29 \
       --model-name my_model_name \
       --cad-data-file ~/Documents/my_model.obj \
       --cad-data-format obj
   1f0f2b7c1f0f4b0a9a1c4b6b0a5b0f2b
   $ vws wait-for-model-target-dataset-generated \
       --client-id "$MODEL_TARGET_CLIENT_ID" \
       --client-secret "$MODEL_TARGET_CLIENT_SECRET" \
       --dataset-uuid 1f0f2b7c1f0f4b0a9a1c4b6b0a5b0f2b
   completed_at: '2026-08-14 12:00:00+00:00'
   created_at: '2026-08-14 11:59:00+00:00'
   dataset_uuid: 1f0f2b7c1f0f4b0a9a1c4b6b0a5b0f2b
   error: null
   eta: null
   status: done
   warning: null
   $ vws download-model-target-dataset \
       --client-id "$MODEL_TARGET_CLIENT_ID" \
       --client-secret "$MODEL_TARGET_CLIENT_SECRET" \
       --dataset-uuid 1f0f2b7c1f0f4b0a9a1c4b6b0a5b0f2b \
       --output ~/Documents/my_dataset.zip
   $ vws delete-model-target-dataset \
       --client-id "$MODEL_TARGET_CLIENT_ID" \
       --client-secret "$MODEL_TARGET_CLIENT_SECRET" \
       --dataset-uuid 1f0f2b7c1f0f4b0a9a1c4b6b0a5b0f2b
   $

.. skip doccmd[shellcheck]: end

Use ``--dataset-type advanced`` with each of these commands for an advanced dataset.
To give more than one model, or to give guide views, describe the models in a JSON file and give it with ``--models-file``:

.. code-block:: json

   {
     "models": [
       {
         "name": "my_model_name",
         "cadDataUrl": "https://example.com/my_model.zip",
         "cadDataFormat": "OBJ",
         "views": [
           {
             "name": "front",
             "guideViewPosition": {
               "rotation": [0, 0, 0, 1],
               "translation": [0, 0, -1.5]
             }
           }
         ]
       }
     ]
   }
