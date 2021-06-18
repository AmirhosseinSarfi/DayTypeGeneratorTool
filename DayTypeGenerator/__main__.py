import ConfigurableOptions as conf
import DayTypeGenerator as dtg
import argparse
import streamlit as st


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Day-Type Generation by flow/speed time profiles')

    st.title(parser.description)
    st.sidebar.title("Configuration Panel")

    argOptions = conf.parseArgument(parser)
    if conf.checkArgument(argOptions):
        st.balloons()
        dtg.run(argOptions)
    else:
        print("CONFIGURATION ERROR(s): review them!")
