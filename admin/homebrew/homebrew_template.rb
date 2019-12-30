class {class_name} < Formula
  include Language::Python::Virtualenv

  url "{archive_url}"
  head "{head_url}"
  homepage "{homepage_url}"
  depends_on "python3"
  depends_on "pkg-config"

{resource_stanzas}

  def install
    ENV["_SETUPTOOLS_SCM_VWS_CLI_FALLBACK"] = "{version_str}"
    virtualenv_install_with_resources
  end
end
