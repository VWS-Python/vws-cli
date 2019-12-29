Usage example
-------------

.. code:: sh

   $ vws add-target \
       --server-access-key $SERVER_ACCESS_KEY \
       --server-secret-key $SERVER_SECRET_KEY \
       --name my_image_name \
       --width 2 \
       --image ~/Documents/my_image.png \
       --application-metadata $(echo "my_metadata" | base64) \
       --active-flag true
   03b99df0-78cf-4b01-b929-f1860d4f8ed1
   $ vws --help
   ...
   $ vuforia-cloud-reco my_image.jpg \
       --max-num-results 5 \
       --include-target-data none
   - target_id: b60f60121d37418eb1de123c381b2af9
   - target_id: e3a6e1a216ad4df3aaae1f6dd309c800
   $
