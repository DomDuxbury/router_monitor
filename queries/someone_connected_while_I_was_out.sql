INSERT into alerts SELECT 'someone_connected_while_I_was_out'
from router
WHERE not owner_is_home
AND num_extra_clients = 1
