<div align="center">

# Jobbergate Agent Charmed Operator

A [Juju](https://juju.is) operator for jobbergate-agent - the job submission daemon of [Jobbergate](https://github.com/omnivector-solutions/jobbergate).

</div>

## Usage

This operator should be used with Juju 3.x or greater.

#### Deploy a minimal Charmed SLURM cluster

```shell
$ juju deploy slurmctld --channel edge
$ juju deploy slurmd --channel edge
$ juju integrate slurmctld:slurmd slurmd:slurmctld
```

## Project & Community

## License

The jobbergate-agent operator is free software, distributed under the Apache Software License, version 2.0. See the [LICENSE](./LICENSE) file for more information.
