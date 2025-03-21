import { Helmet } from "react-helmet";
import Header from "../../components/Header";
import Footer from "../../components/Footer";
import { Flex, Text, Heading, Box, Image, Button, Input, Textarea, Center, Link } from "@chakra-ui/react";
import React from "react";


export default function AboutPage() {
 

  return (
    <>
      <Helmet>
        <title>About | Africa Rangeland Watch</title>
        <meta
          name="description"
          content="Explore the Africa Rangeland Watch to understand and monitor the impact of sustainable rangeland management. Access maps, dashboards, and more."
        />
      </Helmet>

      {/* Main container with background image */}
      <Box
        h={{ md: "60vh", base: "70vh" }}
        bgImage="url('/static/dashboard/dashboard_image5.svg')"
        bgSize="cover"
        bgPosition="center"
        bgRepeat="no-repeat"
        w="100%"
        position="relative"
      >
        {/* Header */}
        <Header />

        {/* Content overlaying the background image */}
        <Flex
          h="100%"
          flexDirection="column"
          justifyContent="center"
          alignItems="center"
          p={{ base: "20px", md: "50px" }}
        >
          {/* Title and Description */}
          <Flex
            flexDirection="column"
            alignItems="center"
            textAlign="center"
            maxW={{ base: "90%", md: "60%" }}
            mb={{ base: "30px", md: "50px" }}
          >
            <Heading as="h1" fontSize={{ base: "24px", md: "48px" }} color="white" mb="30px">
              About Africa Rangeland Watch
            </Heading>
          </Flex>
        </Flex>
      </Box>

      {/* Section with text below the image */}
      <Box
        bg="gray.100"
        py="50px"
        px="20px"
        textAlign="center"
        height={{ base: "350px", md: "auto" }}
        overflowY="auto"
      >
        <Text fontSize="18px" maxW="60%" mx="auto" color="gray.700">
          Rangeland Explorer is designed to be a rangeland monitoring and decision support tool for
          managers and conservation planners in southern Africa. It originated out of work with Meat
          Naturally in the Uzimbuvu Catchment, Eastern Cape, to gather satellite data on baseline
          rangeland condition variables. Deploying the satellite data in a web application stimulates
          interaction with the data and enhances the insight that can be gained.
          <br />
          <br />
          Rangeland Explorer is designed to be a rangeland monitoring and decision support tool for
          managers and conservation planners in southern Africa. It originated out of work with Meat
          Naturally in the Uzimbuvu Catchment, Eastern Cape, to gather satellite data on baseline
          rangeland condition variables. Deploying the satellite data in a web application stimulates
          interaction with the data and enhances the insight that can be gained.
        </Text>
      </Box>


      {/* Green ribbon section */}
      <Box
        bg="dark_green.800"
        h="322px"
        w="auto"
        display="flex"
        justifyContent="center"
        alignItems="center"
        mb="50px"
      >
        <Text
          fontSize={{ base: "20px", md: "24px" }}
          fontWeight="bold"
          color="white"
          textAlign="center"
        >
          Sustainable Rangeland Management
        </Text>
      </Box>


      {/* The Goal Section */}
      <Box py="50px" textAlign="center">
        <Heading as="h2" fontSize="36px" color="black" fontWeight="bold" mb="30px">
          The Goal
        </Heading>
        <Box py="50px" textAlign="center" bg="white">
          <Text fontSize="18px" color="gray.800" maxW="970px" mx="auto" mb="30px">
            The African Rangeland Watch Platform was developed to allow for easier rangeland monitoring and to be a decision support tool for managers and conservation planners in southern Africa.
          </Text>
        </Box>
        <Flex justify="space-between" wrap="wrap" gap={{ base: "20px", md: "40px" }}>
          {/* Icons with titles */}
          <Box textAlign="center"  justifyContent="center" mb="20px" width={{ base: "100%", md: "23%" }}>
            <Image ml={{base: "100px", md:"130px"}} src="static/images/analytics_icon.svg" boxSize="219px" mb="15px" />
            <Text fontSize="18px" fontWeight="bold" color="black">
              Rangeland Monitoring
            </Text>
          </Box>
          <Box textAlign="center" mb="20px" width={{ base: "100%", md: "23%" }}>
            <Image ml={{base: "100px", md:"130px"}} src="static/images/satelite_icon.svg" boxSize="219px" mb="15px"/>
            <Text fontSize="18px" fontWeight="bold" color="black">
              Gather satellite data on baseline rangeland conditions
            </Text>
          </Box>
          <Box textAlign="center" mb="20px" width={{ base: "100%", md: "23%" }}>
            <Image ml={{base: "100px", md:"110px"}} src="static/images/dashboard_and_reports.svg" boxSize="219px" mb="15px" />
            <Text fontSize="18px" fontWeight="bold" color="black">
              Dashboards and Reporting
            </Text>
          </Box>
          <Box textAlign="center" mb="20px" width={{ base: "100%", md: "23%" }}>
            <Image ml={{base: "100px", md:"120px"}} src="static/images/interactive_map_icon.svg" boxSize="219px" mb="15px" />
            <Text fontSize="18px" fontWeight="bold" color="black">
              Interactive map analysis
            </Text>
          </Box>
        </Flex>
      </Box>


      {/* Impact Reports Section */}
      <Box py="50px" px="20px">
      <Heading as="h2" fontSize="36px" color="black" fontWeight="bold" mb="30px" textAlign="center">
        Impact Reports
      </Heading>

      {/* Flex container centered horizontally */}
      <Flex justify="center">
        <Box width={{ base: "100%", md: "470px" }} mb="20px">
          <Image
            src="/static/images/impact_reports_cover.svg"
            alt="Herding for Health"
            maxWidth="100%"
            height={{ base: "auto", md: "332px" }}
            objectFit="cover"
            display="block"
            margin="0 auto"
          />
        </Box>
      </Flex>

      {/* PDF Link below the image */}
      <Flex justify="center">
        <Box textAlign="center" mt="20px">
          <Link 
            href="/static/CSA-Impact-report-11-04-23_hi-res.pdf" 
            color="black" 
            fontSize="16px" 
            fontWeight="bold" 
            isExternal>
            Conservation South Africa Impact Report 2020-2022
          </Link>
        </Box>
      </Flex>
    </Box>

      {/* Footer */}
      <Footer />
    </>
  );
}
