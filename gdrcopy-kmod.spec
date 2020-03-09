# Copyright (c) 2015-2020, Nicolas Chauvet <kwizart@gmail.com>
# All rights reserved.

%{?!nvidia_kmodsrc_version:
%global nvidia_kmodsrc_version 440.64
}

%if 0%{?fedora}
%global buildforkernels akmod
%global debug_package %{nil}
%endif

Name:           gdrcopy-kmod
Version:        2.0
Release:        1%{?dist}
Summary:        A fast GPU memory copy library based on NVIDIA GPUDirect RDMA technology

License:        MIT
URL:            https://github.com/NVIDIA/gdrcopy
Source0:        %{url}/archive/v%{version}/gdrcopy-%{version}.tar.gz

# Should be supported on ppc64le, but no public driver yet
ExclusiveArch:  x86_64

BuildRequires:  gcc
BuildRequires:  xorg-x11-drv-nvidia-kmodsrc
# get the needed BuildRequires (in parts depending on what we build for)
BuildRequires:  %{_bindir}/kmodtool
%{!?kernels:BuildRequires: buildsys-build-rpmfusion-kerneldevpkgs-%{?buildforkernels:%{buildforkernels}}%{!?buildforkernels:current}-%{_target_cpu} }
# kmodtool does its magic here
%{expand:%(kmodtool --target %{_target_cpu} --repo rpmfusion --kmodname %{name} %{?buildforkernels:--%{buildforkernels}} %{?kernels:--for-kernels "%{?kernels}"} 2>/dev/null) }



%description
While GPUDirect RDMA is meant for direct access to GPU memory from
third-party devices, it is possible to use these same APIs to create
perfectly valid CPU mappings of the GPU memory.

The advantage of a CPU driven copy is the essencially zero latency
involved in the copy process. This might be useful when low latencies
are required.


%prep
# error out if there was something wrong with kmodtool
%{?kmodtool_check}
# print kmodtool output for debugging purposes:
kmodtool  --target %{_target_cpu}  --repo rpmfusion --kmodname %{name} %{?buildforkernels:--%{buildforkernels}} %{?kernels:--for-kernels "%{?kernels}"} 2>/dev/null
%setup -q -c

for kernel_version  in %{?kernel_versions} ; do
  cp -a gdrcopy-%{commit0}/gdrdrv _kmod_build_${kernel_version%%___*}
done

# Needed for nv-p2p.h provided by the nvidia driver
mkdir -p kmodsrc
tar Jxf %{_datadir}/nvidia-kmod-%{nvidia_kmodsrc_version}/nvidia-kmod-%{nvidia_kmodsrc_version}-*.tar.xz -C kmodsrc


%build
for kernel_version in %{?kernel_versions}; do
  pushd _kmod_build_${kernel_version%%___*}
    %make_build -C ${kernel_version##*___} \
      M=${PWD} \
      NVIDIA_SRC_DIR=$(pwd)/../kmodsrc/kernel/nvidia \
      V=1 \
     modules
  popd
done


%install
for kernel_version in %{?kernel_versions}; do
  install -D -m 0755 _kmod_build_${kernel_version%%___*}/gdrdrv.ko %{buildroot}/%{kmodinstdir_prefix}/${kernel_version%%___*}/%{kmodinstdir_postfix}/gdrdrv.ko
done
%{?akmod_install}


%changelog
* Thu Feb 06 2020 Nicolas Chauvet <kwizart@gmail.com> - 2.0-1
- Update to 2.0

* Mon Dec 10 2018 Nicolas Chauvet <kwizart@gmail.com> - 1.4-2
- Add nvidia_kmodsrc_version support

* Fri Dec 07 2018 Nicolas Chauvet <kwizart@gmail.com> - 1.4-1
- Update to 1.4
- Drop support for i686

* Fri Apr 07 2017 Nicolas Chauvet <kwizart@gmail.com> - 1.2-1
- Update to 1.2

* Wed Feb 25 2015 Nicolas Chauvet <kwizart@gmail.com> - 0-1
- Initial spec file
