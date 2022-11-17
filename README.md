# Kepler Estimator

Kepler estimator is a client module to kepler model server running as a sidecar of Kepler exporter.

This python will serve a PowerReequest from model package in Kepler exporter as defined in [estimator.go](https://github.com/sustainable-computing-io/kepler/blob/main/pkg/model/estimate.go) via unix domain socket `/tmp/estimator.sock`.
```go
type PowerRequest struct {
    ModelName       string      `json:"model_name"`
    MetricNames     []string    `json:"metrics"`
    ContainerMetricValues [][]float32 `json:"values"`
    CorePower       []float32   `json:"core_power"`
    DRAMPower       []float32   `json:"dram_power"`
    UncorePower     []float32   `json:"uncore_power"`
    PkgPower        []float32   `json:"pkg_power"`
    GPUPower        []float32   `json:"gpu_power"`
    SelectFilter    string      `json:"filter"`
}
```

#### Patch estimator sidecar to Kepler DaemonSet
```bash
kubectl patch daemonset kepler-exporter --patch-file deploy/patch.yaml
```

#### Local test
1. single process
```bash
python src/estimator_test.py
```
2. server-client test
```bash
python src/estimator.py & \
until [ -e /tmp/estimator.sock ]; do sleep 1; done \
&& python src/estimator_client.py \
&& kill $(ps -eaf|grep "python src/estimator.py" -m 1|awk '{print $2}') 2> /dev/null
```