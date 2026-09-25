class StackMachineInterpreter:
    def __init__(self, instructions):
        self.instructions = instructions
        self.stack = []
        self.variables = {}
        self.labels = {}
        self.call_stack = []
        self.parameters = []
        self.program_counter = 0
        self.return_value = None
        self.current_function = None

        self.build_label_table()

    def build_label_table(self):
        for index, instruction in enumerate(self.instructions):
            parts = instruction.split()

            if len(parts) >= 2 and parts[0] == "LABEL":
                self.labels[parts[1]] = index

    def run(self):
        if "FUNC_main" in self.labels:
            self.program_counter = (
                self.labels["FUNC_main"] + 1
            )
            self.current_function = "main"
        else:
            self.program_counter = 0

        while self.program_counter < len(self.instructions):

            instruction = (
                self.instructions[
                    self.program_counter
                ].strip()
            )

            if not instruction:
                self.program_counter += 1
                continue

            if instruction.startswith(";"):
                self.program_counter += 1
                continue

            self.execute(instruction)

        return self.return_value

    def execute(self, instruction):
        parts = instruction.split()

        if not parts:
            self.program_counter += 1
            return

        opcode = parts[0]

        # -------------------------
        # LABEL
        # -------------------------

        if opcode == "LABEL":

            label = parts[1]

            if label.startswith("FUNC_"):

                function_name = label[5:]

                if function_name != self.current_function:
                    self.skip_function_body(
                        function_name
                    )
                    return

            self.program_counter += 1
            return

        # -------------------------
        # LOAD
        # -------------------------

        if opcode == "LOAD":

            value = instruction[5:].strip()

            self.stack.append(
                self.get_value(value)
            )

            self.program_counter += 1
            return

        # -------------------------
        # STORE
        # -------------------------

        if opcode == "STORE":

            variable = (
                instruction[6:].strip()
            )

            value = (
                self.stack.pop()
                if self.stack
                else 0
            )

            self.variables[variable] = value

            self.program_counter += 1
            return

        # -------------------------
        # ARITHMETIC
        # -------------------------

        if opcode in {
            "ADD",
            "SUB",
            "MUL",
            "DIV",
            "MOD"
        }:

            self.execute_arithmetic(opcode)

            self.program_counter += 1
            return

        # -------------------------
        # COMPARISON
        # -------------------------

        if opcode in {
            "EQ",
            "NE",
            "LT",
            "GT",
            "LE",
            "GE"
        }:

            self.execute_comparison(opcode)

            self.program_counter += 1
            return

        # -------------------------
        # LOGICAL
        # -------------------------

        if opcode in {
            "AND",
            "OR"
        }:

            self.execute_logical(opcode)

            self.program_counter += 1
            return

        # -------------------------
        # NEGATION
        # -------------------------

        if opcode == "NEG":

            value = self.stack.pop()

            self.stack.append(-value)

            self.program_counter += 1
            return

        # -------------------------
        # NOT
        # -------------------------

        if opcode == "NOT":

            value = self.stack.pop()

            self.stack.append(
                0 if value else 1
            )

            self.program_counter += 1
            return

        # -------------------------
        # GOTO
        # -------------------------

        if opcode == "GOTO":

            label = parts[1]

            self.jump_to(label)

            return

        # -------------------------
        # JZ
        # -------------------------

        if opcode == "JZ":

            label = parts[1]

            condition = (
                self.stack.pop()
                if self.stack
                else 0
            )

            if not condition:
                self.jump_to(label)
            else:
                self.program_counter += 1

            return

        # -------------------------
        # PARAM
        # -------------------------

        if opcode == "PARAM":

            if self.stack:

                value = self.stack.pop()

                self.parameters.append(
                    value
                )

            self.program_counter += 1
            return

        # -------------------------
        # CALL
        # -------------------------

        if opcode == "CALL":

            function_name = parts[1]

            argument_count = 0

            if len(parts) >= 3:

                try:
                    argument_count = int(
                        parts[2]
                    )
                except ValueError:
                    argument_count = 0

            self.execute_call(
                function_name,
                argument_count
            )

            return

        # -------------------------
        # RETURN
        # -------------------------

        if opcode == "RETURN":

            value = (
                self.stack.pop()
                if self.stack
                else 0
            )

            if self.call_stack:

                return_pc, previous_function = (
                    self.call_stack.pop()
                )

                self.stack.append(value)

                self.current_function = (
                    previous_function
                )

                self.program_counter = (
                    return_pc
                )

            else:

                self.return_value = value

                self.program_counter = (
                    len(self.instructions)
                )

            return

        self.program_counter += 1

    # -------------------------------------------------
    # SKIP FUNCTION BODY
    # -------------------------------------------------

    def skip_function_body(self, function_name):

        end_label = (
            f"END_{function_name}"
        )

        if end_label not in self.labels:

            self.program_counter += 1

            return

        self.program_counter = (
            self.labels[end_label] + 1
        )

    # -------------------------------------------------
    # ARITHMETIC
    # -------------------------------------------------

    def execute_arithmetic(self, opcode):

        if len(self.stack) < 2:

            self.stack.append(0)

            return

        right = self.stack.pop()
        left = self.stack.pop()

        if opcode == "ADD":
            result = left + right

        elif opcode == "SUB":
            result = left - right

        elif opcode == "MUL":
            result = left * right

        elif opcode == "DIV":

            if right == 0:
                raise RuntimeError(
                    "Division by zero."
                )

            result = left // right

        elif opcode == "MOD":

            if right == 0:
                raise RuntimeError(
                    "Modulo by zero."
                )

            result = left % right

        else:
            result = 0

        self.stack.append(result)

    # -------------------------------------------------
    # COMPARISON
    # -------------------------------------------------

    def execute_comparison(self, opcode):

        if len(self.stack) < 2:

            self.stack.append(0)

            return

        right = self.stack.pop()
        left = self.stack.pop()

        if opcode == "EQ":
            result = int(left == right)

        elif opcode == "NE":
            result = int(left != right)

        elif opcode == "LT":
            result = int(left < right)

        elif opcode == "GT":
            result = int(left > right)

        elif opcode == "LE":
            result = int(left <= right)

        elif opcode == "GE":
            result = int(left >= right)

        else:
            result = 0

        self.stack.append(result)

    # -------------------------------------------------
    # LOGICAL
    # -------------------------------------------------

    def execute_logical(self, opcode):

        if len(self.stack) < 2:

            self.stack.append(0)

            return

        right = self.stack.pop()
        left = self.stack.pop()

        if opcode == "AND":

            result = int(
                bool(left) and bool(right)
            )

        else:

            result = int(
                bool(left) or bool(right)
            )

        self.stack.append(result)

    # -------------------------------------------------
    # FUNCTION CALL
    # -------------------------------------------------

    def execute_call(
        self,
        function_name,
        argument_count
    ):

        label = (
            f"FUNC_{function_name}"
        )

        if label not in self.labels:

            raise RuntimeError(
                f"Function '{function_name}' "
                f"not found."
            )

        return_address = (
            self.program_counter + 1
        )

        self.call_stack.append(
            (
                return_address,
                self.current_function
            )
        )

        function_arguments = []

        for _ in range(argument_count):

            if self.parameters:

                function_arguments.append(
                    self.parameters.pop()
                )

        function_arguments.reverse()

        self.assign_function_parameters(
            function_name,
            function_arguments
        )

        self.current_function = (
            function_name
        )

        self.program_counter = (
            self.labels[label] + 1
        )

    # -------------------------------------------------
    # FUNCTION PARAMETERS
    # -------------------------------------------------

    def assign_function_parameters(
        self,
        function_name,
        arguments
    ):

        label = (
            f"FUNC_{function_name}"
        )

        if label not in self.labels:
            return

        index = self.labels[label] + 1

        argument_index = 0

        while index < len(self.instructions):

            instruction = (
                self.instructions[index]
            )

            if instruction.startswith(
                "; param "
            ):

                parts = instruction.split()

                if len(parts) >= 4:

                    parameter_name = (
                        parts[3]
                    )

                    if argument_index < len(
                        arguments
                    ):

                        self.variables[
                            parameter_name
                        ] = arguments[
                            argument_index
                        ]

                        argument_index += 1

            elif instruction.startswith(
                "LABEL "
            ):

                break

            index += 1

    # -------------------------------------------------
    # JUMP
    # -------------------------------------------------

    def jump_to(self, label):

        if label not in self.labels:

            raise RuntimeError(
                f"Label '{label}' not found."
            )

        self.program_counter = (
            self.labels[label] + 1
        )

    # -------------------------------------------------
    # GET VALUE
    # -------------------------------------------------

    def get_value(self, value):

        value = value.strip()

        try:
            return int(value)

        except ValueError:
            pass

        if (
            len(value) >= 2
            and value[0] == '"'
            and value[-1] == '"'
        ):

            return value[1:-1]

        if value == "true":
            return 1

        if value == "false":
            return 0

        if value in self.variables:

            return self.variables[value]

        return 0

    # -------------------------------------------------
    # PRINT STATE
    # -------------------------------------------------

    def print_state(self):

        print("\nInterpreter State:")
        print("-----------------")

        if not self.variables:

            print("No variables.")

        else:

            for name, value in (
                self.variables.items()
            ):

                print(
                    f"{name} = {value}"
                )

        print(
            f"Stack = {self.stack}"
        )

        if self.return_value is not None:

            print(
                f"Return value = "
                f"{self.return_value}"
            )
