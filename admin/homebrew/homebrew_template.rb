class {class_name} < Formula
  include Language::Python::Virtualenv

  url "{archive_url}"
  head "{head_url}"
  homepage "{homepage_url}"
  depends_on "python@3.9"
  depends_on "pkg-config"

{resource_stanzas}

  def install
    virtualenv_install_with_resources
  end
end
