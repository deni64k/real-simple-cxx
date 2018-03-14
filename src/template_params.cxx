#include <iostream>
#include <boost/current_function.hpp>
#include <boost/type_index.hpp>

using boost::typeindex::type_id_with_cvr;

template <typename T>
static
void Run([[maybe_unused]] PARAM_TYPE t) {
  std::cout << '|' << type_id_with_cvr<T>().pretty_name();
  std::cout << '|' << type_id_with_cvr<decltype(t)>().pretty_name();
  std::cout << '|' << BOOST_CURRENT_FUNCTION;
}

int main(int argc, char **argv) {
  INIT_CLAUSE;

  Run(IN_WRAPPER(IN_TYPE, in_val));

  return 0;
}
