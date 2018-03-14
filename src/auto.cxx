#include <iostream>
#include <boost/type_index.hpp>

using boost::typeindex::type_id_with_cvr;

static
void Run() {
  INIT_CLAUSE;

  AUTO               x = in_val;
  decltype(auto)     y = in_val;
  decltype((in_val)) z = in_val;

  std::cout << '|' << type_id_with_cvr<decltype(x)>().pretty_name();
  std::cout << '|' << type_id_with_cvr<decltype(y)>().pretty_name();
  std::cout << '|' << type_id_with_cvr<decltype(z)>().pretty_name();
}

int main(int argc, char **argv) {
  Run();

  return 0;
}
