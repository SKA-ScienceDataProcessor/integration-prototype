# Mock workflow stage for testing Execution Control components

### Testing

To test the docker file

```bash
docker run skasip/mock_workflow_stage:test '{"duration": 20}'
```

Test if compose file works

```bash
docker stack deploy -c docker-compose.test.yml st
```
